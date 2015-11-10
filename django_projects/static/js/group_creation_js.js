$(document).ready(function() {
    // Create the sampleList DataTable
    var sampleList = $('#sample_list').DataTable({
        dom: '<"tablewrapper"fti>',
        paging: false,
        select: {
            style: 'os', // Allow user to shift- and ctrl/cmd- click for multiselection
            blurable: true // All selections are deselected on loss of focus
        },
        columnDefs: [
            {
                targets: [0],
                visible: false,
                searchable: false
            }
        ]
    });

    // JS for group name --------------------------------------------------------------------------------------------

    // Stop the user from using the Return key to submit the form prematurely.
    // We want the user to use the submit button.
    $('.noSubmitOnEnter').keypress(function(e) {
        if (e.which == 13) e.preventDefault();
    });

    // group name validation
    $('#samples_attribute_form').validate({
        rules: {
            name: {
                required: true,
                pattern: /^[^0-9\s][\Sa-zA-Z_-]+$/
            }
        },
        messages: {
            name: {
                required: "Please enter an experiment name",
                pattern: "Must start with a letter, contain more than 1 letter, and contain no whitespace"
            }
        }
    });

    //---------------------------------------------------------------------------------------------------------------

    // JS for adding a new attribute field --------------------------------------------------------------------------

    var numberAttributes = 0; // The number of attributes (experimental conditions) created by the user

    var numberSampleAttributes = 0; // The number of sampleAttributes created by the user

    // Disable the add condition button until there is legal input in the field
    validateAttributeName();
    $('#attribute_name_field').keyup(validateAttributeName);

    function validateAttributeName() {

        var putative_attribute_name = $('#attribute_name_field').val();
        var re = /^[^0-9\s][\Sa-zA-Z_-]+$/;

        if (putative_attribute_name.length == 0) {
            $('#create_attribute').prop('disabled', true);
        } else if (re.test(putative_attribute_name)) {
            $('#create_attribute').prop('disabled', false);
        } else {
            $('#create_attribute').prop('disabled', true);
        }
    }

    // Buttons for attributes in the samples_attributes column
    // Add the selected samples to the selected condition
    $('#samples_attributes').on('click', '.add_samples', function(e) {
        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');
        var attributeName = $(attributeDiv).prop('id');

        attributeDiv.find('.sample_placeholder').remove();

        // Add the samples in the selected table rows
        // to the attributeDiv
        var samplesToAssign = sampleList.rows({
            selected: true
        });

        var sampleData = sampleList.rows({
            selected: true
        }).data();

        $.each(sampleData, function (_, sample) {
             // Increment the TOTAL_FORMS variable for django's formset
            numberSampleAttributes++;
            $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);
            console.log("Added! Number of Sample Attribute Pairings = " + numberSampleAttributes);

            // Clone the template field
            var newSample = $($('#sampleattribute_form_template').clone().html().replace(/__prefix__/g, numberSampleAttributes));
            newSample.css('display', 'none');
            newSample.appendTo(attributeDiv.children('.panel-body'));
            $('[name="samplesattributes-' + numberSampleAttributes + '-sample"]').val(sample[0]);
            $('[name="samplesattributes-' + numberSampleAttributes + '-attribute"]').val(attributeName);

            attributeDiv.find('ol').append('<li data-form_id=' + numberSampleAttributes + ' data-sample_id=' + sample[0] + ' data-polarity="' + sample[2] + '"><div class="sample_name" style="display:inline;">' + sample[1] + ' </div><a href="#" class="remove_sample">(Remove)</a></li>');

        });

        samplesToAssign.remove().draw();
    });

    function removeSample(sampleAsLi) {
        // Takes a sample of the form <li data-form_id=FORM_ID data-sample_id=SAMPLE_ID data-polarity=POLARITY><div class="sample_name">SAMPLE_NAME</div></li>
        // Adds this information to the sampleList table
        // Remves the sampleAsLi from the attribute div

        // liElId = current list element Id
        var liElId = parseInt($(sampleAsLi).attr('data-sample_id'));
        var polarity = $(sampleAsLi).attr('data-polarity');
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-sample"]').remove();
        $('[name="samplesattributes-' + $(sampleAsLi).text()[0] + '-attribute"]').remove();
        sampleList.row.add([liElId, $(sampleAsLi).children('.sample_name').text(), polarity]).draw();
        sampleAsLi.remove();
        numberSampleAttributes--;
        $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);
        console.log("Subtracted! Number of Sample Attribute Pairings = " + numberSampleAttributes);
    }

    // Erase one sample button
    $('#samples_attributes').on('click', '.remove_sample', function(e) {
        // Remove the selected sample from the attribute div and replace it into the sampleList table
        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');

        removeSample($(this).parents('li'));

        if (attributeDiv.has('li').length == 0) {
            attributeDiv.children('.panel-body').append('<p class="sample_placeholder">No samples</p>');
        }


    });

    // Erase all samples button
    $('#samples_attributes').on('click', '.remove_samples', function(e) {
        // Remove all samples from the attribute div and replace them into the sampleList table

        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');
        var liEls = attributeDiv.find('li');

       	$(liEls).each(function(_, sampleAsLi) {
            removeSample(sampleAsLi);
        });

        attributeDiv.find('ol')
            .empty()
            .before('<p class="sample_placeholder">No samples</p>');

    });

    $('#samples_attributes').on('click', '.delete_condition', function(e) {
        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');

        // First, remove all the samples assigned to this condition and return them to the sampleList table
        var liEls = attributeDiv.find('li');

       	$(liEls).each(function(_, sampleAsLi) {
            removeSample(sampleAsLi);
        });

        // Then delete the attribute div
        attributeDiv.remove();

    })

    // Create a div in the samples_attributes column for the new attribute.
    // Provides controls to add samples to the attribute, delete the attribute, and empty it of its samples.
    $('#create_attribute').click(function(e) {
        e.preventDefault();

        // Increment the attributes-TOTAL_FORMS variable to keep track of the number of forms
        // for the django management_form
        numberAttributes++;
        $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);

        // Build up a div to go into the sample attributes column, which contains a hidden django sample attribute form. Present a nicely formatted div containing the details of the attribute and assigned samples.
        var attributeName = $('#attribute_name_field').val();
        var addButton = '<button class="btn btn-sm btn-default add_samples"><span class="glyphicon glyphicon-plus"></span></button>';
        var emptyButton = '<button class="btn btn-sm btn-default remove_samples"><span class="glyphicon glyphicon-eject"></span></button>';
        var deleteButton = '<button class="btn btn-sm btn-danger delete_condition"><span class="glyphicon glyphicon-trash"></button>';
        var attributeControls = '<div class="btn-group pull-right">' + addButton + emptyButton +  deleteButton + '</div>';
        var attributeDiv = $('<div class="panel panel-info attribute" id="' + attributeName + '"><div class="panel-heading clearfix">' + attributeControls + '<h2 class="panel-title">' + attributeName+ '</h2>' + '</div><div class="panel-body"><ol></ol><p class="sample_placeholder">No samples</p></div></div>');

        // Clone the template field and update its index accordingly for the management_form.
        // Hide it, and add it to the new attributeDiv
        var newField = $($('#attribute_form_template').clone().html().replace(/__prefix__/g, numberAttributes));
        newField.val(attributeName);
        newField.css('display', 'none');
        attributeDiv.append(newField);

        // Remove the placeholder text if it exists, and add the new attributeDiv into the DOM.
        if ($('#attributes').find('#no_attribute_placeholder').length == 0) {
            attributeDiv.appendTo('#samples_attributes');
        } else {
            $('#samples_attributes')
                .empty()
                .append(attributeDiv);
        }

        $('#attribute_name_field').val(''); // Clear the input for the next attribute
        $('#create_attribute').prop('disabled', true); // Return the button to disabled state

    });

});
