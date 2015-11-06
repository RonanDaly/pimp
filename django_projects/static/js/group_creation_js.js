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

    //---------------------------------------------------------------------------------------------------------------

    // JS for adding a new attribute field --------------------------------------------------------------------------

    var numberAttributes = 0; // The number of attributes (experimental conditions) created by the user

    var numberSampleAttributes = 0; // The number of sampleAttributes created by the user

    // Disable the add condition button until there is input in the field
    validateAttributeName();
    $('#attribute_name_field').keyup(validateAttributeName);
    function validateAttributeName() {
        if ($('#attribute_name_field').val().length == 0) {
            $('#create_attribute').prop('disabled', true);
        } else {
            $('#create_attribute').prop('disabled', false);
        }
    }

    // Controls for attributes in the samples_attributes column
    // Add the selected samples to the selected condition
    $('#samples_attributes').on('click', '.add_samples', function(e) {
        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');
        var attributeName = $(attributeDiv).prop('id');
        console.log(attributeName);

        $('#sample_placeholder').remove();

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

            // Clone the template field
            var newSample = $($('#sampleattribute_form_template').clone().html().replace(/__prefix__/g, numberSampleAttributes));
            newSample.css('display', 'none');
            newSample.appendTo(attributeDiv.children('.panel-body'));
            $('[name="samplesattributes-' + numberSampleAttributes + '-sample"]').val(sample[0])
            $('[name="samplesattributes-' + numberSampleAttributes + '-attribute"]').val(attributeName);

            console.log('adding sampleID = ' + $('[name="samplesattributes-' + numberSampleAttributes + '-sample"]').val());
            console.log('adding attribute name = ' + $('[name="samplesattributes-' + numberSampleAttributes + '-attribute"]').val());
            attributeDiv.find('ol').append('<li data-form_id=' + numberSampleAttributes + ' data-sample_id=' + sample[0] + '>' + '<div class="sample_name">' + sample[1] + '</div>' + ' (' + '<div class="sample_polarity">' + sample[2] +  '</div>)</li>');

        });
        samplesToAssign.remove().draw();
    });

    // Erase all samples button
    // Need to make a more general reusable function for removing single, and multiple samples
    $('#samples_attributes').on('click', '.remove_sample', function(e) {
        e.preventDefault();

        var attributeDiv = $(this).parents('.panel');
        var liEls = attributeDiv.find('li');

       	$(liEls).each(function (_, listItem) {
            // liElId = current list element Id
            var liElId = parseInt($(listItem).attr('data-sample_id'));
            $('[name="samplesattributes-' + $(listItem).attr('data-form_id') + '-sample"]').remove();
            $('[name="samplesattributes-' + $(listItem).text()[0] + '-attribute"]').remove();
            console.log($(listItem).children('.sample_name').text());
            sampleList.row.add([liElId, $(listItem).children('.sample_name').text(), $(listItem).children('.sample_polarity').text()]).draw();
        });

        attributeDiv.find('ol').empty();
    });

    // Create a div in the samples_attributes column for the new attribute.
    // Provides controls to add samples to the attribute, delete the attribute, and empty it of its samples.
    $('#create_attribute').click(function(e) {

        // Increment the attributes-TOTAL_FORMS variable to keep track of the number of forms
        // for the django management_form
        numberAttributes++;
        $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);

        // Build up a div to go into the sample attributes column, which contains a hidden django sample attribute form. Present a nicely formatted div containing the details of the attribute and assigned samples.
        var attributeName = $('#attribute_name_field').val(); // // Get the name of the attribute. Need to validate the attribute name
        var addButton = '<button class="btn btn-sm btn-default add_samples"><span class="glyphicon glyphicon-plus"></span></button>';
        var emptyButton = '<button class="btn btn-sm btn-default remove_sample"><span class="glyphicon glyphicon-eject"></span></button>';
        var deleteButton = '<button class="btn btn-sm btn-danger delete_condition"><span class="glyphicon glyphicon-trash"></button>';
        var attributeControls = '<div class="btn-group pull-right">' + addButton + emptyButton +  deleteButton + '</div>';
        var attributeDiv = $('<div class="panel panel-info attribute" id="' + attributeName + '"><div class="panel-heading clearfix">' + attributeControls + '<h2 class="panel-title">' + attributeName+ '</h2>' + '</div><div class="panel-body"><ol></ol><p id="sample_placeholder">No samples added yet</p></div></div>');

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


    //---------------------------------------------------------------------------------------------------------------


    //// Variables and functions for attribute_construction div
    ////$('#attribute_construction').show();
    ////$('.sample_assignment').hide();
    //
    //// The number of attributes (experimental conditions) created by the user
    //
    //$('#attribute_construction').on('click', '.add_condition_field', function (e) {
    //    // Add a new field to the attributes form. Incremement Django's management_form
    //    // form-TOTAL_FORMS variable to compensate for this, and ensure all forms are
    //    // handled.
    //
    //    e.preventDefault();
    //
    //    // Increment the TOTAL_FORMS variable for django's formset
    //    numberAttributes++;
    //    $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);
    //
    //    // Clone the template field, clearing any cloned input.
    //    // Increment the id and name values of the fields
    //    // Django's formset form numbering starts at 0, whereas
    //    // numberAttributes starts at 0; use (numberAttributes - 1)
    //    // to update the form index
    //    var newField = $($('#attribute_form_template').clone().html().replace(/__prefix__/g, numberAttributes - 1));
    //    newField.find('input').val('');
    //    newField.appendTo('#attribute_fields');
    //
    //    // For all except the last input-group, change the input-group-btn
    //    // button to have remove classes
    //    $('#attribute_fields').find('.add_condition_field:not(:last)')
    //        .removeClass('btn-success add_condition_field')
    //        .addClass('btn-danger remove_field')
    //        .html('<span class="glyphicon glyphicon-minus"></span>');
    //
    //});
    //
    //$('#attribute_fields').on('click', '.remove_field', function (e) {
    //    // Delete the field and reduce the form-TOTAL_FORMS variable for the
    //    // django management_form
    //    e.preventDefault();
    //
    //    // remove the field
    //    $(this).parents('.input-group:first').remove();
    //
    //    // Decrement the number of attributes and update the managerform variable
    //    numberAttributes--;
    //    $('[name=attributes-TOTAL_FORMS]').val(numberAttributes);
    //
    //    // Everytime an attribute field is removed the id and name values of all
    //    // fields must be reset, in case the attribute field removed is not == #attribute_field:last
    //    var attributeFieldDoms = $('#attribute_fields').find('.input-group');
    //
    //    attributeFieldDoms.each(function(i, attributeField) {
    //        // Update the id and names of each remaining attributeField
    //        var updated = $(attributeField).html().replace(/(attributes-)[0-9]+(-)/g, '$1' + i  + '$2');
    //        $(attributeField).empty();
    //        $(attributeField).append(updated);
    //    });
    //
    //});
    //
    //$('#attribute_form').on('click', '#go_to_assignment', function (e) {
    //    e.preventDefault();
    //    $('#experiment_name').empty().append($('#group_input').val());
    //
    //    var attributeFieldDoms = $('#attribute_fields').find('input');
    //
    //    createAttributesDivs(attributeFieldDoms);
    //
    //    $('#attribute_construction').hide();
    //    $('.sample_assignment').show();
    //
    //});
    //
    //$('.sample_assignment').on('click', '#go_to_create_attributes', function (e) {
    //    console.log("pressed!");
    //    e.preventDefault();
    //    $('.sample_assignment').hide();
    //    $('#attribute_construction').show();
    //});
    //
    //// variables and functions for sample_assignment div
    //function createAttributesDivs(attributeFieldDoms) {
    //    // TODO: Disable buttons when nothing is selected
    //    $('#attributes').children('div').remove();
    //
    //
    //    // Add the divs for each attribute
    //    var numberSampleAttributes = 0; // number of assignments of samples to attributes
    //
    //    $.each(attributeFieldDoms, function (_, attribute) {
    //        // create a div and add and empty buttons
    //        var addButton = '<button class="btn btn-sm btn-success add"><span class="glyphicon glyphicon-plus"></span></button>';
    //        var emptyButton = '<button class="btn btn-sm btn-danger empty"><span class="glyphicon glyphicon-trash"></button>';
    //        var attributeControls = '<div class="btn-group pull-right">' + addButton + emptyButton + '</div>';
    //        var attributeDiv = '<div class="panel panel-default" id="' + attribute.value + '"><div class="panel-heading clearfix">' + attributeControls + '<h2 class="panel-title pull-left">' + attribute.value + '</h2></div><div class="panel-body"><ol></ol></div></div>';
    //        $('#attributes').append(attributeDiv);
    //
    //    });
    //
    //    $('.add').click(function (e) {
    //        // Add the selected samples to the selected condition
    //        e.preventDefault();
    //
    //        // Begin adding of sample to attribute code
    //
    //        // Increment the TOTAL_FORMS variable for django's formset
    //        numberSampleAttributes++;
    //        $('[name=samplesattributes-TOTAL_FORMS]').val(numberAttributes);
    //
    //        // Clone the template field, clearing any cloned input.
    //        // Increment the id and name values of the fields
    //        // Django's formset form numbering starts at 0, whereas
    //        // numberAttributes starts at 0; use (numberAttributes - 1)
    //        // to update the form index
    //        var newField = $($('#attribute_form_template').clone().html().replace(/__prefix__/g, numberAttributes - 1));
    //        newField.find('input').val('');
    //        newField.appendTo('#attribute_fields');
    //
    //        // For all except the last input-group, change the input-group-btn
    //        // button to have remove classes
    //        $('#attribute_fields').find('.add_condition_field:not(:last)')
    //            .removeClass('btn-success add_condition_field')
    //            .addClass('btn-danger remove_field')
    //            .html('<span class="glyphicon glyphicon-minus"></span>');
    //
    //        // end adding of sample to attribute code
    //
    //
    //        var attributeDiv = $(this).parents('.panel');
    //        // Add the samples in the selected table rows
    //        // to the attributeDiv
    //        var samplesToAssign = sampleList.rows({
    //            selected: true
    //        });
    //        var sampleData = sampleList.rows({
    //            selected: true
    //        }).data();
    //        $.each(sampleData, function (_, sample) {
    //            attributeDiv.find('ol').append('<li data-id=' + sample[0] + '>' + sample[1] + '</li>');
    //
    //        });
    //        samplesToAssign.remove().draw();
    //    });
    //
    //    $('.empty').click(function (e) {
    //        e.preventDefault();
    //        var attributeDiv = $(this).parents('.panel');
    //        var liEls = attributeDiv.find('li');
    //
    //       	$(liEls).each(function (_, listItem) {
    //            // liElId = current list element Id
    //            var liElId = parseInt($(listItem).attr('data-id'));
    //            sampleList.row.add([liElId, $(listItem).text()[0]]).draw();
    //        });
    //        attributeDiv.find('ol').empty();
    //    });
    //}
});