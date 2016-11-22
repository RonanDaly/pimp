__author__ = 'Scott Greig'

from frank.models import *
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from decimal import *
from suds.client import Client, WebFault
import time
import jsonpickle
import re
from django.conf import settings
from subprocess import call, CalledProcessError
import os
from django.db.models import Max
from urllib2 import URLError


MASS_OF_AN_PROTON = 1.00727645199076


class MassBankQueryTool:

    """
    Class to query the external API for MassBank - can also be used when MassBank installed on internal server
    """

    def __init__(self, annotation_query_id, fragmentation_set_id):
        """
        Constructor for the MassBankQuery Tool
        :param annotation_query_id: Integer id of a AnnotationQuery model instance
        :param fragmentation_set_id: Integer id of a FragmentationSet model instance
        """

        # Check to ensure these id'd correspond to existing model instances
        try:
            self.annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
            self.annotation_tool = self.annotation_query.annotation_tool
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except TypeError:
            raise

    def get_mass_bank_annotations(self):

        """
        Method to form a query to massbank for retrieval of candidate annotations
        :return: True:  Boolean indicating the completion of the query
        """

        print 'Forming MassBank Query Spectra'
        # The query spectra comprise grouping of parent ions and there associated fragments
        query_spectra = self._generate_query_spectra()
        # While MassBank allows for 'pooled' query spectra to be sent, it was determined that it would
        # be better to send the positive and negative spectra separately to improve candidate annotations.
        positive_spectra = None
        negative_spectra = None
        if query_spectra:
            positive_spectra = query_spectra['positive_spectra']
            negative_spectra = query_spectra['negative_spectra']
        else:
            raise ValidationError('No spectra to be queried')
        try:
            print 'Querying MassBank...'
            # Queries are only sent to MassBank if there are spectra to be sent
            if len(positive_spectra) > 0:
                print 'Sending Positive Spectra...'
                # The positive spectra query is then sent to MassBank
                positive_annotations = self._query_mass_bank(positive_spectra, 'Positive')
                if positive_annotations:
                    print 'Populating Positive Annotations...'
                    # Candidate annotations are populated into the database
                    self._populate_annotations_table(positive_annotations)
                    print 'Positive Annotations Populated...'
            if len(negative_spectra) > 0:
                print 'Sending Negative Spectra...'
                # The negative spectra query is then sent to MassBank
                negative_annotations = self._query_mass_bank(negative_spectra, 'Negative')
                if negative_annotations:
                    print 'Populating Negative Annotations...'
                    # The candidate annotations are populated into the database
                    self._populate_annotations_table(negative_annotations)
                    print 'Negative Annotations Populated...'
        except WebFault:
            raise
        except URLError:
            raise
        except AttributeError:
            raise
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except ValidationError:
            raise
        except InvalidOperation:
            raise
        print 'MassBank Query Completed Successfully'
        return True

    def _generate_query_spectra(self):

        """
        Method to format the query to be sent to MassBank
        :return: query_spectra: A dictionary containing both the 'positive_spectra' and 'negative_spectra'
                                of the fragmentation set.
        """

        # Retrieve all peak associated with this fragmentation set
        sample_peak_qset = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
        total_number_of_peaks = len(sample_peak_qset)
        # If there are no peaks then there is no query_spectra
        if total_number_of_peaks == 0:
            return None
        number_of_msn_levels = sample_peak_qset.aggregate(Max('msn_level'))
        number_of_msn_levels = number_of_msn_levels['msn_level__max']
        positive_samples_query = []
        negative_samples_query = []
        # Each msn level is considered in turn
        for level in range(1, number_of_msn_levels):
            # Get all the peaks in the level
            peaks_in_msn_level = sample_peak_qset.filter(msn_level=level)
            # For each peak in the msn level
            for peak in peaks_in_msn_level:
                # Retrieve the polarity and slug
                # As the slug is unique, it is used to associate a query spectra back to the parent ion
                polarity = peak.source_file.polarity
                peak_identifier = peak.slug
                # Retrieve the fragments associated with the precursor peak
                fragmented_peaks = sample_peak_qset.filter(parent_peak=peak)
                # Only if there are fragments is the spectra added to the query
                if len(fragmented_peaks) > 0:
                    spectrum_query_string = list('Name:'+peak_identifier+';')
                    for fragment in fragmented_peaks:
                        # The fragmentation spectra consists of mass and intensity pairs
                        spectrum_query_string.append(''+str(fragment.mass)+','+str(fragment.intensity)+';')
                    if polarity == 'Positive':
                        positive_samples_query.append(''.join(spectrum_query_string))
                    elif polarity == 'Negative':
                        negative_samples_query.append(''.join(spectrum_query_string))
        query_spectra = {
            'positive_spectra': positive_samples_query,
            'negative_spectra': negative_samples_query,
        }
        return query_spectra

    def _query_mass_bank(self, query_spectra, polarity):

        """
        Method to send the query to mass bank and retrieve the candidate annotation as a results set
        :return: mass_bank_results: The result set returned by mass_bank
        """

        # Check to ensure there are spectra to send to mass bank
        if len(query_spectra) == 0:
            return None
        # The search parameters specified by the user are in the annotation query
        mass_bank_parameters = jsonpickle.decode(self.annotation_query.annotation_tool_params)
        # MassBank provides a service to email the recipiant upon completion of query
        mail_address = mass_bank_parameters['mail_address']
        # Spectra can be queried against pre-specified instrument types
        instruments = mass_bank_parameters['instrument_types']
        # The polarity of the spectra is included - although can be 'both'
        # However, positive and negative were separated to ensure candidate annotations match the polarity of
        # the query spectra
        ion = polarity
        # The default parameters for the tool itself are retrieved from the AnnotationTool
        # These can be modified in the population script (populate_pimp.py)
        search_parameters = jsonpickle.decode(self.annotation_tool.default_params)
        # Note - MassBank batch search of spectra is type '1'
        search_type = search_parameters['type']
        # The address required for the client is the MassBank server, again see population script, can be changed
        # there for change over to local install
        client_address = search_parameters['client']

        client_address = "http://massbank.ufz.de:80/api/services/MassBankAPI?wsdl"

        client = Client(client_address)
        try:
            # Submit the batch search to MassBank, a job ID is returned
            submission_response = client.service.execBatchJob(
                search_type,
                mail_address,
                query_spectra,
                instruments,
                ion,
            )
        except WebFault:
            raise
        except URLError:
            # Corresponds to a failure in internet connectivity
            raise
        job_id = submission_response
        job_list = [job_id]
        job_status = None
        for repetition in range(0, 200):
            # At present, the celery worker will sleep for 5 minutes between job status queries to MassBank,
            # for a total of 200 attempts, however, queries could occur at a higher frequency when a local install
            # is available. The 200 repetitions is due to the frequency with which the external service can be
            # busy at present. Therefore, jobs do not process immediately upon submission.
            time.sleep(300)
            try:
                # Query MassBank for the status of the job
                job_status = client.service.getJobStatus(job_list)
                print job_status
            except WebFault:
                raise
            except URLError:
                raise
            if job_status['status'] == 'Completed':
                break
        # If, at the end of the repetitions, MassBank has failed to complete the job in the alloted time
        if job_status['status'] != 'Completed':
            raise ValidationError('MassBank Service Unavailable or Busy, No Results Returned.')
        else:  # MassBank completed the query
            try:
                # If the job has been completed, then retrieve the results from MassBank
                response3 = client.service.getJobResult(job_list)
            except WebFault:
                raise
            mass_bank_results = response3
        return mass_bank_results

    def _populate_annotations_table(self, annotation_results):

        """
        Method to populate the database tables of the application using the results generated from massbank
        :param annotation_results:  The results set returned by MassBank (in python this is a dictionary)
        :return: True   Indicates that the results of the query have been successfully added to the database
        """

        for result_set_dict in annotation_results:
            # A result_set corresponds to the candidate annotations for one peak's fragmentation spectra
            peak_identifier_slug = result_set_dict['queryName']
            print 'Processing...'+peak_identifier_slug
            try:
                annotations = result_set_dict['results']
                # The candidate annotations are stored in a list
            except AttributeError:
                # If the candidate annotations have come back incorrectly formatted, this may be thrown
                # if the dictionary does not contain these
                raise
            try:
                # Get the peak the candidate annotations are associated with
                peak_object = Peak.objects.get(slug=peak_identifier_slug)
            except MultipleObjectsReturned:
                raise
            except ObjectDoesNotExist:
                raise
            for each_annotation in annotations:
                # The elements of the annotation title are separated by a '; '
                elements_of_title = re.split('; ', each_annotation['title'])
                try:
                    # Create a compound in the database if one does not already exist
                    compound_object = Compound.objects.get_or_create(
                        formula=each_annotation['formula'],
                        exact_mass=each_annotation['exactMass'],
                        name=elements_of_title[0],
                        # The first element of the title is always the compound name
                    )[0]
                    # And add the compound to the CompoundAnnotationTool table
                    compound_annotation_tool = CompoundAnnotationTool.objects.get_or_create(
                        compound=compound_object,
                        annotation_tool=self.annotation_tool,
                        annotation_tool_identifier=each_annotation['id'],
                    )[0]
                    annotation_mass = Decimal(each_annotation['exactMass'])
                    difference_in_mass = peak_object.mass-annotation_mass
                    mass_match = False
                    # By default the mass of the annotation does not match that of the peak
                    # However, if the difference in mass is within the mass of an electron, it may
                    # be considered a match in mass
                    if abs(difference_in_mass) <= MASS_OF_AN_PROTON:
                        mass_match = True
                    # Try and obtain the adduct and collision energy from the description
                    adduct_label = None
                    collision_energy = None
                    """
                    Important to note that due to the open source nature of MassBank, there is a significant
                    variation in the format the candidate annotations are returned in. The adduct is typically
                    The last element of the title, however, this is not the case in all annotations. In addition,
                    the collision energy, may or may not be included, and the units of measurement may be either
                    eV or a percentage depending on the instrument manufacturer.

                    While eV is an exact measure of the collision energy, the % is a normalised collision energy
                    used by Thermo devices. Therefore, collision energy will be stored as a string including value and
                    units.

                    Therefore, the application will try and obtain the adduct and collision energy, where possible
                    to do so.
                    """
                    for element in elements_of_title:
                        if element.startswith('[M'):
                            adduct_label = element
                        if element.startswith('CE'):
                            try:
                                collision_energy = re.split('CE:', element)[1].strip()
                            except IndexError:
                                pass
                    # Finally create the candidate annotation in the database
                    CandidateAnnotation.objects.create(
                        compound=compound_object,
                        peak=peak_object,
                        confidence=each_annotation['score'],
                        annotation_query=self.annotation_query,
                        difference_from_peak_mass=difference_in_mass,
                        mass_match=mass_match,
                        adduct=adduct_label,
                        instrument_type=elements_of_title[1],
                        collision_energy=collision_energy,
                        additional_information=each_annotation['title']
                    )
                except ValidationError:
                    # If the annotation cannot be formatted to a model instance, it may be ignored
                    print 'Invalid Annotation - Annotation Ignored'
                    pass
                except MultipleObjectsReturned:
                    raise
                except InvalidOperation:
                    # If the annotation cannot be formatted to a model instance, it may be ignored
                    print 'Invalid Annotation - Annotation Ignored'
                    pass
        return True

class SIRIUSQueryTool:
    """
    Class to query SIRIUS
    """
    print 'We at least got to here'
    def __init__(self, annotation_query_id,fragmentation_set_id):


        print 'In querytool constructor'
        try:
            # Check to ensure the annotation query, associated fragmentation set and annotation tool exist
            self.annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
            self.fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
            self.annotation_tool = self.annotation_query.annotation_tool

        except ObjectDoesNotExist:
            raise
        except MultipleObjectsReturned:
            raise
        except TypeError:
            raise
        # Determine suitable names for both the query file and sirius output files
        self.query_file_name = os.path.join(
            os.path.dirname(settings.BASE_DIR),
            'pimp',
            'frank',
            'SIRIUSQueryFiles',
            str(self.annotation_query.id)+'.mgf'
        )
        self.sirius_output_file_name = os.path.join(
            os.path.dirname(settings.BASE_DIR),
            'pimp',
            'frank',
            'SIRIUSQueryFiles',
            str(self.annotation_query.id)+'_sirius_out.txt'
        )


    @property
    def get_sirius_annotations(self):

        sirius_parameters = jsonpickle.decode(self.annotation_query.annotation_tool_params)

        # Retrieve all peak associated with this fragmentation set
        all_peaks = Peak.objects.filter(fragmentation_set=self.fragmentation_set)

        #Parents have msn level of 1.
        all_parents = all_peaks.filter(msn_level=1)
        total_number_of_parents = len(all_parents)


        #Annotation parameters that can be used throughout - but perhaps not listed here?
        max_number_of_hits = sirius_parameters['max_hits']
        profile = sirius_parameters['profile_type']
        max_ppm = sirius_parameters['max_ppm']
        output_f = sirius_parameters['output_format']

        #current_script_dir = os.path.dirname(os.path.realpath(__file__))


        """
        Method to retrieve candidate annotations from SIRIUS
        :return True:   Boolean denoting the successfull completion of a query for annotations
        """
        print 'total number of parents', total_number_of_parents
        i = 0

        #This is the children of the parent peaks and we are going to pass it to the write_mgf file.

        # Send the parent and associated children to Sirius.
        #This while loop lets us go through the method 10 times for testing.

        try:

            for parent in all_parents:



                fragmented_peaks = all_peaks.filter(parent_peak=parent)
                polarity = parent.source_file.polarity
                #Just an interger to check that all parents are looped through

                print 'Writing MGF File...'

                # get the mgf file for use in SIRIUS from the parent and associated children
                mgf = self._write_sirius_mgf_file(parent, fragmented_peaks, polarity)
                print mgf


                # Call Sirius on the temporary mgf file.
                data =self._query_sirius(mgf, polarity, max_ppm, output_f, profile, max_number_of_hits)
                if data is not None:
                    print
                    print "JSON OUTPUT"
                    pp = pprint.PrettyPrinter(depth=4)
                    pp.pprint(data)
                    # Generate the subprocess call, ensuring that the user-specified parameters are included
                    # Read in the Sirius output file and populate the database
                    print 'Populating List'
                    self._populate_sirius_annotation_list(data, parent, fragmented_peaks)
                    print 'Annotations Completed'
                    i=i+1
                    print 'i=',i
                    #if i >1:
                    #    break
                        # # Finally upon completion, delete both the temporary files for NIST
                        # os.remove(self.nist_output_file_name)
                        # os.remove(self.query_file_name)
        except IOError:#

            raise
        except OSError:
            raise
        except ValueError:
            raise
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except Warning:
            raise

        return True


    def _write_sirius_mgf_file(self, parent, fragmented_peaks, polarity):

        """
        Method to write the fragmentation spectra to a MGF file format for querying of SIRIUS
        :return: String (mgf-styled)

        This will send one parent and its child to Sirius.

        MGF file format for SIRIUS queries is as follows
        Each spectrum can contain many spectra starting with "BEGIN IONS" and ending with "END IONS"
        Peak_pairs: m/z intensity
        PEPMASS: parent peak
        CHARGE: 1+ OR 1-
        MSLEVEL: 1 for MS spectra and 2 for MS/MS

        """
        #Most likely don't need these here - just used to print and check parameters
        parent_identifier = parent.slug
        parent_mass = parent.mass
        parent_intensity = parent.intensity

        # Number of fragments associated with the parent peak.

        numb_frags = len(fragmented_peaks)
        print 'number of fragments are', numb_frags

        #Print out a list of parameters to make sure that we are on the right track
        #print " ",parent_identifier, parent_mass, parent_intensity, numb_frags

        print "pID %4s m/z %5.5f int %.4e n_frags %2d\t" %(parent_identifier, parent_mass, parent_intensity, numb_frags )

        # create temp mgf file, start by initailising mgf.

        mgf=""
        mgf += "BEGIN IONS\n"
        mgf += "PEPMASS=" + str(parent_mass) + "\n"
        mgf += "MSLEVEL=1\n"
        if polarity == "Positive":
            mgf += "CHARGE=1+\n"
        elif polarity == "Negative":
            mgf += "CHARGE=1-\n"
        mgf += str(parent_mass) + " " + str(parent_intensity) + "\n"
        mgf += "END IONS\n"
        mgf += "\n"
        mgf += "BEGIN IONS\n"
        mgf += "PEPMASS=" + str(parent_mass) + "\n"
        mgf += "MSLEVEL=2\n"
        if polarity == "Positive":
            mgf += "CHARGE=1+\n"
        elif polarity == "Negative":
            mgf += "CHARGE=1-\n"

        #If there are fragments associated with the parent peak.
        if numb_frags > 0:
            #For each fragment in the list of fragment peaks
            for fragment in fragmented_peaks:
                frag_mass = fragment.mass
                frag_intensity = fragment.intensity
                mgf += str(frag_mass) + " " + str(frag_intensity) + "\n"
            mgf += "END IONS\n"
            mgf += "\n"
        return mgf


    def _query_sirius(self,mgf, polarity, max_ppm, output_f, profile, max_number_of_hits):

        """
        Send the .mgf file to query Sirius and return the results.
        :rtype : Sirius_results, the results returned by Sirius.
         """
        # run sirius on the temp mgf file
        print 'In Sirius query'
        starting_dir = os.getcwd()

        try:
            #Generate a temporary file and directory for the .mgf file
            temp_dir = tempfile.mkdtemp()
            fd, temp_filename = tempfile.mkstemp(suffix=".mgf", text=True)
            current_script_dir = os.path.dirname(os.path.realpath(__file__))
            with open(temp_filename, "w") as text_file:
                text_file.write(mgf)
            # detect OS and pick the right executable for SIRIUS
            system = platform.system()
            arch = platform.architecture()[0]

            print 'system, arch. current_dir=',system, arch, current_script_dir

            #Karen's mac specific parameters
            valid_platform = False
            if system == 'Darwin': #Might be able to put this together with linux.
                if arch == '64bit':
                    valid_platform = True
                    sirius_dir = 'sirius_3_0_3_linux64'
                    sirius_exec= 'sirius'
            elif system == 'Linux':
                if arch == '64bit':
                    valid_platform = True
                    sirius_dir = 'linux64'
                    sirius_exec = 'sirius'
            elif system == 'Windows':
                if arch == '32bit':
                    valid_platform = True
                    sirius_dir = 'win32'
                    sirius_exec = 'sirius.exe'
            elif arch == '64bit':
                valid_platform = True
                sirius_dir = 'win64'
                sirius_exec = 'sirius.exe'

            if not valid_platform:
                raise ValueError(system + " " + arch + " is not supported")
            print 'found valid dir and executable', sirius_dir, sirius_exec
            # Send the information to Sirius

            full_exec_dir = os.path.join(current_script_dir, sirius_dir)
            full_exec_path = os.path.join(full_exec_dir, sirius_exec)
            os.chdir(full_exec_dir)
            if polarity == "Positive":
                adduct = "[M+H]+"
            elif polarity == "Negative":
                adduct = "[M-H]-"

            sirius_args = [full_exec_path,
                           '-p', profile,
                           '-s', 'omit', #Q. Should this be a user choice??
                           '-c', str(max_number_of_hits),
                           '--ppm-max ',str(max_ppm),
                           '-i', adduct,
                           '-O', output_f,
                           '-o', temp_dir,
                           temp_filename]
            print 'Sirius Args are', sirius_args

            #Run Sirius command with the defined sirius arguements

            subprocess.check_call(sirius_args)

            # read the first file produced by sirius
            files = sorted(os.listdir(temp_dir))



            #List error - ask about this code.
            #KmcL this needs fixed if the data is not of the format json
            print
            first_filename = os.path.join(temp_dir, files[0])
            sirius_data = open(first_filename).read()
            data = json.loads(sirius_data)

        except subprocess.CalledProcessError, e:
            print
            print "SIRIUS produced error: " + str(e)
            data = None

            #break # stop the loop
        except IndexError, e:
            print "SIRIUS returned nothing: " + str(e)
            data = None


        finally:
            # close temp input file and remove it
            os.close(fd)
            os.remove(temp_filename)
            # delete all the temp output files produced by sirius
            shutil.rmtree(temp_dir)
            # restore current directory
            os.chdir(starting_dir)

        return data


    # Passing in fargmented_peaks as children into this method
    # A method to populate the annotation table.
    def _populate_sirius_annotation_list(self, sirius_data, parent, children):


        min_score=0.01 #Hardwired minimum acceptable score - should this be somewhere else? as a final?

        overall_score = sirius_data['annotations']['score']['total']
        fragment_annotations = sirius_data['fragments']

        if overall_score > min_score:

            # loop over all annotations and find matching entry
            for f_annotation in fragment_annotations:


                formula_annot = f_annotation['molecularFormula']
                annot_mass = Decimal(f_annotation['mz'])
                #Find which peak object fragment corresponds to, if any.

                correct_peak = parent
                mass_error = (Decimal(1e6)*abs(correct_peak.mass-annot_mass)/annot_mass) #ppm mass error

                for child in children:
                    #If the difference in the child peak < diff in the parent peak, correct peak is child peak
                    child_mass_error = (Decimal(1e6)*abs(child.mass-annot_mass)/annot_mass)
                    if child_mass_error < mass_error:
                        mass_error = child_mass_error
                        correct_peak = child

                #Store if error difference less than 5 ppm.
                if mass_error < 5:

                    #Create a compound in the database if one does not already exist
                    compound_object_list = Compound.objects.get_or_create(formula=formula_annot, exact_mass=annot_mass, name=formula_annot)
                    compound_object = compound_object_list[0]


                    # And add the compound to the CompoundAnnotationTool table
                    CompoundAnnotationTool.objects.get_or_create(
                        compound=compound_object,
                        annotation_tool=self.annotation_tool,
                        annotation_tool_identifier='na',
                    )

                    # Finally add the candidate annotation to the database
                    new_candidate_annotation = CandidateAnnotation.objects.create(
                        compound=compound_object,
                        peak=correct_peak,
                        confidence=f_annotation['score'],
                        annotation_query=self.annotation_query,
                        difference_from_peak_mass=correct_peak.mass-annot_mass,
                        mass_match=True
                    )

                    #Set the preferred anootation for the child peak as the one with the greatest confidence.
                    if correct_peak in children:
                        #If a preferred canditate annotation is set
                        if correct_peak.preferred_candidate_annotation:
                            #Check if the confidence of this peak is greater.
                            if new_candidate_annotation.confidence > correct_peak.preferred_candidate_annotation.confidence:
                                correct_peak.preferred_candidate_annotation=new_candidate_annotation
                                correct_peak.save()
                        #Else not set, set the preferred annotation
                        else:
                            correct_peak.preferred_candidate_annotation=new_candidate_annotation
                            correct_peak.save()

                return True

#A method to collect the annotations for both MS1 and MS2 peaks.
def _collect_sirius_annotations(self):
    return True


class NISTQueryTool:

    """
    Class representing the NIST spectral reference library
    """

    def __init__(self, annotation_query_id):
        """
        Constructor for the NIST query tool
        """

        try:
            # Check to ensure the annotation query, associated fragmentation set and annotation tool exist
            self.annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
            self.fragmentation_set = self.annotation_query.fragmentation_set
            self.annotation_tool = self.annotation_query.annotation_tool
        except ObjectDoesNotExist:
            raise
        except MultipleObjectsReturned:
            raise
        except TypeError:
            raise
        # Determine suitable names for both the query file and nist output files
        
        #Local directory name
        self.query_nist_dir = os.path.join(
            os.path.dirname(settings.BASE_DIR),

            'pimp',
            'frank',
            'NISTQueryFiles',
            str(self.annotation_query.id)+'.msp'
        )
        self.nist_output_file_name = os.path.join(
            os.path.dirname(BASE_DIR),
            'pimp',
            'frank',
            'NISTQueryFiles',
            str(self.annotation_query.id)+'_nist_out.txt'
        )

    def get_nist_annotations(self):

        """
        Method to retrieve candidate annotations from the NIST spectral reference library
        :return True:   Boolean denoting the successfull completion of a query for annotations
        """

        try:
            print 'Writing MSP File...'
            # Write the query spectrum to a temporary file
            self._write_nist_msp_file()
            # Generate the subprocess call, ensuring that the user-specified parameters are included
            print 'Generating NIST subprocess call...'
            nist_query_call = self._generate_nist_call()
            print 'Querying NIST...'
            # Query the NIST reference database, generating an output file
            self._query_nist(nist_query_call)
            print 'Populating Annotations Table...'
            # Read in the NIST output file and populate the database
            self._populate_annotation_list()
            print 'Annotations Completed'
            # Finally upon completion, delete both the temporary files for NIST
            # os.remove(self.nist_output_file_name)
            # os.remove(self.query_file_name)
        except IOError:
            raise
        except OSError:
            raise
        except ValueError:
            raise
        except MultipleObjectsReturned:
            raise
        except ObjectDoesNotExist:
            raise
        except Warning:
            raise
        return True

    def _generate_nist_call(self):

        """
        Method to construct the appropriate call to the NIST subprocess
        :return: nist_query_call:   A String call to NIST containing the user specified search parameters

        """

        # From the annotation query - get the user selected parameters
        nist_parameters = jsonpickle.decode(self.annotation_query.annotation_tool_params)
        tool_parameters = jsonpickle.decode(self.annotation_tool.default_params)
        library_list = nist_parameters['library']
        # Check that the user has specified at least one library for the query
        if len(library_list) == 0:
            raise ValueError('No NIST Libraries were selected by the user')
        max_number_of_hits = nist_parameters['max_hits']
        # The maximum number of hits NIST will return must be between 1 and 100
        if max_number_of_hits < 1 or max_number_of_hits > 100:
            raise ValueError('The maximum number of hits exceeds specified bounds (between 1 and 100)')
        search_type = nist_parameters['search_type']
        # The call to NIST is performed via Wine
        nist_query_call = ["wine",
                           tool_parameters['source'],
                           search_type,
                           "/HITS",
                           str(max_number_of_hits),
                           '/PATH',
                           tool_parameters['library_path']]
        # Add the libraries which are to be included in the search to NIST
        for library in library_list:
            if library == 'mainlib':
                nist_query_call.extend(['/MAIN', 'mainlib'])
            elif library == 'nist_msms':
                nist_query_call.extend(['/LIB', 'nist_msms'])
            elif library == 'nist_msms2':
                nist_query_call.extend(['/LIB', 'nist_msms2'])
            elif library == 'nist_ri':
                nist_query_call.extend(['/LIB', 'nist_ri'])
            elif library == 'replib':
                nist_query_call.extend(['/REPL', 'replib'])
        additional_parameters = ['/INP', self.query_file_name,
                                 '/OUT', self.nist_output_file_name]
        nist_query_call.extend(additional_parameters)
        return nist_query_call

    def _query_nist(self, nist_query_call):

        """
        Method to perform a subprocess call to NIST
        :param nist_query_call: A string containing the call to NIST
        :return: True:  A Boolean to denote the completion of the call to NIST
        """

        try:
            # Make the call to NIST to write the candidate annotations to the output file
            call(nist_query_call)
        except CalledProcessError:
            raise
        except OSError:
            raise
        # Finally check to see if the call was successfull and the output file exists
        if os.path.isfile(self.nist_output_file_name) is False:
            raise Warning('NIST failed to write the output file')
        return True

    def _write_nist_msp_file(self):

        """
        Method to write the fragmentation spectra to a MSP file format for querying of NIST
        :return: True:  A boolean to confirm the output file was written successfully
        """

        """
        MSP file format for NIST queries is as follows
        #   NAME: name_of_query
        #   DB#: name_of_query
        #   Precursormz: mass_of_parent_ion (required for 'G', but not 'M' type search)
        #   Comments: nothing
        #   Num Peaks: number_of_peaks_in_spectra
        #   mass    intensity   ### For each of the peaks in the spectra
        """

        experiment_protocol = self.fragmentation_set.experiment.detection_method
        include_precursor_mz = False
        if experiment_protocol.name == 'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition':
            include_precursor_mz = True
        # Due to the use of a pseudo ms1 peak in the gcms datasets, the stored precursor is not a genuine precursor
        # Therefore, its mass should not be submitted to NIST which takes this into account.
        # Conversely, massbank's search API does not
        output_file = None
        try:
            # Open new MSP file for writing
            with open(self.query_file_name, "w") as output_file:
                # Retrieve all the peaks in the fragmentation set
                peaks_in_fragmentation_set = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
                # Determine if there are peaks to be written to the MSP file
                if len(peaks_in_fragmentation_set) < 1:
                    raise ValueError('No peaks found in fragmentation set')
                # Determine the number of msn levels
                number_of_msn_levels = peaks_in_fragmentation_set.aggregate(Max('msn_level'))
                number_of_msn_levels = number_of_msn_levels['msn_level__max']
                for level in range(1, number_of_msn_levels):
                    # Get all peaks in the current msn level
                    peaks_in_msn_level = peaks_in_fragmentation_set.filter(msn_level=level)
                    # For each peak in the level
                    for peak in peaks_in_msn_level:
                        fragmentation_spectra = peaks_in_fragmentation_set.filter(parent_peak=peak)
                        # Only write the spectra to the file if it has fragmentation spectra
                        if len(fragmentation_spectra) > 0:
                            if include_precursor_mz:
                                output_file.write('NAME: '+peak.slug+'\nDB#: ' + str(peak.id) +
                                                  '\nComments: None\nPrecursormz:' + str(peak.mass) +
                                                  '\nNum Peaks: ' + str(len(fragmentation_spectra)) + '\n')
                            else:
                                output_file.write('NAME: ' + peak.slug + '\nDB#: ' + str(peak.id) +
                                                  '\nComments: None\nNum Peaks: ' +
                                                  str(len(fragmentation_spectra)) + '\n')
                            for fragment in fragmentation_spectra:
                                output_file.write(str(fragment.mass)+' ' + str(fragment.intensity) + '\n')
                            output_file.write('\n')
        except IOError:
            raise
        finally:
            # Using 'with' should close the file but make sure
            if output_file.closed is False:
                output_file.close()
        return True

    def _populate_annotation_list(self):

        """
        Method to populate the candidate annotations into the database from NIST
        :return: True:  A boolean denoting the successfull populatation of the candidate annotations
        """

        # Get the peaks for the fragmentation set from the database
        peaks_in_fragmentation_set = Peak.objects.filter(fragmentation_set=self.fragmentation_set)
        input_file = None
        try:
            with open(self.nist_output_file_name, "r") as input_file:
                # Open the NIST output file
                current_parent_peak = None
                # For each line which does not begin in a comment (in NIST.txt this is indicated by '>')
                for line in (line for line in input_file if not line.startswith('>')):
                    try:
                        # Due to use of wine,'NIST' uses a distinct encoding which alters the greek letters
                        line = line.decode('cp437').encode('utf-8', errors='strict')
                    except UnicodeError as ue:
                        print ue.message
                        # This type of error results from NIST output files using cp437 characters
                        # which seems to only impact on greek letters...therefore, exception is passed
                        pass
                    if line.startswith('Unknown:'):
                        # These lines indicate the title of the query spectra - i.e. the peak slug identifier
                        line_tokens = [token.split() for token in line.splitlines()]
                        # Retrieves the slug of the parent peak
                        parent_ion_slug = line_tokens[0][1]
                        if parent_ion_slug.startswith('<<') and parent_ion_slug.endswith('>>'):
                            # The parent_ion_slug is encased in <<peak_slug>>, so create substring
                            parent_ion_slug = parent_ion_slug[2:-2]
                        try:
                            current_parent_peak = peaks_in_fragmentation_set.get(slug=parent_ion_slug)
                            print 'Populating Annotations For: '+current_parent_peak.slug
                        except MultipleObjectsReturned:
                            raise
                        except ObjectDoesNotExist:
                            raise
                    elif line.startswith('Hit'):
                        # Get the description of the annotation
                        annotation_description = line.splitlines()[0]
                        string_annotation_attributes = re.findall('<<(.*?)>>', annotation_description, re.DOTALL)
                        # The compound name is the first attribute encased in << >>
                        compound_name = string_annotation_attributes[0]
                        # The compound formula is the second
                        compound_formula = string_annotation_attributes[1]
                        # Retrieve the confidence value
                        annotation_confidence = Decimal(re.findall(
                            'Prob: (.*?);', annotation_description, re.DOTALL)[0])
                        # Try to retrieve the CAS code, a unique compound identifier
                        compound_cas = re.findall('CAS:(.*?);', annotation_description, re.DOTALL)[0]
                        if compound_cas == '0-00-0':
                            # For some compounds in the NIST database, the cas code is unknown
                            compound_cas = None
                        # Get the mass of the compound
                        compound_mass = Decimal(re.findall('Mw: (.*?);', annotation_description, re.DOTALL)[0])
                        # And the unique identifier NIST uses to identify the compound
                        compound_annotation_tool_identifier = re.findall('Id: (\d+).', annotation_description)[0]
                        try:
                            # Try to add the compound to the database
                            compound_object = Compound.objects.get_or_create(
                                formula=compound_formula,
                                exact_mass=compound_mass,
                                name=compound_name,
                                cas_code=compound_cas,
                            )[0]
                            # And form the association with the NIST Annotation Tool
                            compound_annotation_tool = CompoundAnnotationTool.objects.get_or_create(
                                compound=compound_object,
                                annotation_tool=self.annotation_tool,
                                annotation_tool_identifier=compound_annotation_tool_identifier,
                            )[0]
                            # Determine the difference in mass between the candidate annotation and the measured mass
                            difference_in_mass = current_parent_peak.mass-compound_mass
                            mass_match = False
                            # If the mass of the candidate annotation is within that of an electron,
                            # it is considered a match
                            if abs(difference_in_mass) <= MASS_OF_AN_PROTON:
                                mass_match = True
                            # Add the candidate annotation to the database
                            CandidateAnnotation.objects.create(
                                compound=compound_object,
                                peak=current_parent_peak,
                                confidence=annotation_confidence,
                                annotation_query=self.annotation_query,
                                difference_from_peak_mass=difference_in_mass,
                                mass_match=mass_match,
                                additional_information=annotation_description
                            )
                        except ValidationError as ve:
                            print ve.message
                            # In the event of a validation error, simply ignore this candidate annotation
                            # and resume trying to add the remaining annotations
                            pass
                        except MultipleObjectsReturned:
                            raise
        except IOError:
            raise
        finally:
            # Using 'with' should close the file but make sure
            if input_file.closed is False:
                input_file.close()
        return True