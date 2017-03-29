function main() {

    // Create the sampleList DataTable
    // same as group_creation
    var sampleList = $('#sample_list').DataTable({
        dom: '<"tablewrapper"fti>',
        paging: false,
        scrollY: '350px',
        scrollCollapse: true,
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

    // disable all Add buttons initially
    $('#qc-add-btn').prop('disabled', true);
    $('#blank-add-btn').prop('disabled', true);
    $('#standard-add-btn').prop('disabled', true);

    sampleList.on( 'select', function(e, dt, type, indexes) {

        // get selected rows
        var sampleData = sampleList.rows({
            selected: true
        }).data();

        // check if selected rows contains mzxml or csv
        var has_mzxml = false;
        var has_csv = false;
        $.each(sampleData, function (_, sample) {

            var filename = sample[1];
            var extension = filename.split('.').pop();
            if (extension.toUpperCase() === 'MZXML') {
                has_mzxml = true;
            } else if (extension.toUpperCase() === 'CSV') {
                has_csv = true;
            }

            // console.log("Selected " + filename + ', extension ' + extension +
            //     ', has_mzxml ' + has_mzxml + ', has_csv ' + has_csv);

        });

        if (has_mzxml && has_csv) {
            $('#qc-add-btn').prop('disabled', false);
            $('#blank-add-btn').prop('disabled', false);
            $('#standard-add-btn').prop('disabled', false);
        } else if (has_mzxml) {
            $('#qc-add-btn').prop('disabled', false);
            $('#blank-add-btn').prop('disabled', false);
            $('#standard-add-btn').prop('disabled', true);
        } else if (has_csv) {
            $('#qc-add-btn').prop('disabled', true);
            $('#blank-add-btn').prop('disabled', true);
            $('#standard-add-btn').prop('disabled', false);
        }

    }).on( 'deselect', function (e, dt, type, indexes) {

        $('#qc-add-btn').prop('disabled', true);
        $('#blank-add-btn').prop('disabled', true);
        $('#standard-add-btn').prop('disabled', true);

    });

    $('[data-toggle=tooltip]').tooltip(); // Set the tooltips

    var numberSampleAttributes = $('[name=samplesattributes-TOTAL_FORMS]').val();

    // This function update the index of the elements when we add/remove comparisons, if not updated, the django formset will not be parsed properly in the view when the html form is submited !Important
    // It is also used for validating the form with jquery validate
    function updateElementIndex(el, prefix, ndx) {
        var id_regex = new RegExp('(' + prefix + '-\\d+-)');
        var replacement = prefix + '-' + ndx + '-';
        // If the element has an html attribute "for", then update it
        if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex,replacement));
        // If the element has an html attribute "id", then update it
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        // If the element has an html attribute "name", then update it
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    }

    function removeSample(sampleAsLi) {
        // Remove a sample from the attribute div and return it to the sampleList table.

        // Takes a sample of the form <li data-form_id=FORM_ID data-sample_id=SAMPLE_ID data-polarity=POLARITY><div class="sample_name">SAMPLE_NAME</div></li>
        // Adds this information to the sampleList table
        // Remves the sampleAsLi from the attribute div

        // liElId = current list element Id
        var liElId = parseInt($(sampleAsLi).attr('data-sample_id'));
        var polarity = $(sampleAsLi).attr('data-polarity');
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-projfile"]').parent('.item').remove();
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-projfile"]').remove();
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-attribute"]').remove();
        sampleList.row.add([liElId, $(sampleAsLi).children('.sample_name').text(), polarity]).draw();
        sampleAsLi.remove();
        numberSampleAttributes--;
        $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);

        var forms = $('.item');
        var i = 0;

        // Go through the forms and set their indices, names and IDs
        for (formCount = forms.length; i < formCount; i++) {

            console.log(i);
            // update the id and name of the textarea with the right index
            $(forms.get(i)).find("textarea").each(function() {
                // if we are updating the id of the projfile tag, also update the data-form_id of the li tag 
                if ($(this).attr('id').split('-')[2] === 'projfile') {
                    $('li[data-sample_id="' + $(this).val() + '"]').attr('data-form_id',i);
                }
                updateElementIndex(this, 'samplesattributes', i);
            });

            // update the for of the label with the right index
            $(forms.get(i)).find("label").each(function() {
                updateElementIndex(this, 'samplesattributes', i);
            });
        }
    }

    function validateSample(button_id, sampleData) {

        valid = true
        $.each(sampleData, function (_, sample) {

            var filename = sample[1];
            var extension = filename.split('.').pop();
            if (button_id === 'qc-add-btn' && extension.toUpperCase() === 'CSV') {
                valid = false;
            } else if (button_id == 'blank-add-btn' && extension.toUpperCase() === 'CSV') {
                valid = false;
            } else if (button_id == 'standard-add-btn' && extension.toUpperCase() === 'MZXML') {
                valid = false;
            }

        });
        return valid;

    }

    // Buttons for attributes in the samples_attributes column
    $('#samples_attributes')
        .on('click', '.add_samples', function(e) { // Add the selected samples to the selected condition

            e.preventDefault();

            // Add the samples in the selected table rows
            // to the attributeDiv
            var samplesToAssign = sampleList.rows({
                selected: true
            });

            // Check if the user selected any samples - if not, don't try and add any to the attribute
            if (samplesToAssign[0].length > 0) {

                var attributeDiv = $(this).parents('.panel');
                var attributeName = $(attributeDiv).prop('id');
                attributeDiv.find('.sample_placeholder').remove();

                var sampleData = sampleList.rows({
                    selected: true
                }).data();

                var button_id = e.currentTarget.id;
                valid = validateSample(button_id, sampleData);
                if (valid) {

                    $.each(sampleData, function (_, sample) {
                        // Increment the TOTAL_FORMS variable for django's formset
                        numberSampleAttributes++;
                        $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);

                        // Clone the template field
                        var itemDiv = $('<div class="item"></div>');
                        itemDiv.css('display', 'none');
                        var newSample = $($('#sampleattribute_form_template').clone().html().replace(/__prefix__/g, (numberSampleAttributes - 1)));
                        newSample.css('display', 'none');
                        newSample.appendTo(itemDiv);
                        itemDiv.appendTo(attributeDiv.children('.panel-body'));
                        $('[name="samplesattributes-' + (numberSampleAttributes - 1) + '-projfile"]').val(sample[0]);
                        $('[name="samplesattributes-' + (numberSampleAttributes - 1) + '-attribute"]').val(attributeName);

                        attributeDiv.find('ol').append('<li class="list-group-item" data-form_id=' + (numberSampleAttributes - 1) + ' data-sample_id=' + sample[0] + ' data-polarity="' + sample[2] + '"><div class="sample_name" style="display:inline;">' + sample[1] + '</div><span class="pull-right"><a href="#" class="remove_sample btn btn-xs btn-default"><span class="glyphicon glyphicon-remove"></span></a></span></li>');
                    });

                    samplesToAssign.remove().draw();

                } else {
                    var msg = "Cannot insert these samples into the calibration group.";
                    var msg_div = $('#error-msg').text(msg).show();
                }

            } else { // no samples were selected when the add sample button was pushed
                console.warn("The user tried to add samples to the attribute, but no samples were selected!");
            }

        })
        .on('click', '.remove_sample', function(e) { // Erase one sample button
            // Remove the selected sample from the attribute div and replace it into the sampleList table
            e.preventDefault();

            var attributeDiv = $(this).parents('.panel');

            removeSample($(this).parents('li'));

            if (attributeDiv.has('li').length == 0) {
                attributeDiv.children('.panel-body').append('<p class="sample_placeholder">No samples</p>');
            }
        })
        .on('click', '.remove_samples', function(e) { // Erase all samples button
            // Remove all samples from the attribute div and replace them into the sampleList table

            e.preventDefault();

            var attributeDiv = $(this).parents('.panel');
            var liEls = attributeDiv.find('li');

            // Check if there are any samples (liEls) in the attribute to remove
            if (liEls.length > 0) {
                $(liEls).each(function(_, sampleAsLi) {
                removeSample(sampleAsLi);
                });

                attributeDiv.find('ol')
                    .empty()
                    .before('<p class="sample_placeholder">No samples</p>');
            } else { // There are no samples to remove from the attribute.
                console.warn("The user tried to remove all samples from the attribute, but the attribute contained no samples!");
            }

        });
}

$(document).ready(main);