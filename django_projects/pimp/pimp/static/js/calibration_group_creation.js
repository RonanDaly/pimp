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

    $('[data-toggle=tooltip]').tooltip(); // Set the tooltips

    var numberSampleAttributes = 0;

    function removeSample(sampleAsLi) {
        // Remove a sample from the attribute div and return it to the sampleList table.

        // Takes a sample of the form <li data-form_id=FORM_ID data-sample_id=SAMPLE_ID data-polarity=POLARITY><div class="sample_name">SAMPLE_NAME</div></li>
        // Adds this information to the sampleList table
        // Remves the sampleAsLi from the attribute div

        // liElId = current list element Id
        var liElId = parseInt($(sampleAsLi).attr('data-sample_id'));
        var polarity = $(sampleAsLi).attr('data-polarity');
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-sample"]').remove();
        $('[name="samplesattributes-' + $(sampleAsLi).attr('data-form_id') + '-attribute"]').remove();
        sampleList.row.add([liElId, $(sampleAsLi).children('.sample_name').text(), polarity]).draw();
        sampleAsLi.remove();
        numberSampleAttributes--;
        $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);
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

                $.each(sampleData, function (_, sample) {
                    // Increment the TOTAL_FORMS variable for django's formset
                    numberSampleAttributes++;
                    $('[name=samplesattributes-TOTAL_FORMS]').val(numberSampleAttributes);

                    // Clone the template field
                    var newSample = $($('#sampleattribute_form_template').clone().html().replace(/__prefix__/g, (numberSampleAttributes - 1)));
                    newSample.css('display', 'none');
                    newSample.appendTo(attributeDiv.children('.panel-body'));
                    $('[name="samplesattributes-' + (numberSampleAttributes - 1) + '-projfile"]').val(sample[0]);
                    $('[name="samplesattributes-' + (numberSampleAttributes - 1) + '-attribute"]').val(attributeName);

                    attributeDiv.find('ol').append('<li data-form_id=' + (numberSampleAttributes - 1) + ' data-sample_id=' + sample[0] + ' data-polarity="' + sample[2] + '"><div class="sample_name" style="display:inline;">' + sample[1] + ' </div><a href="#" class="remove_sample">(Remove)</a></li>');
                });

                samplesToAssign.remove().draw();
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