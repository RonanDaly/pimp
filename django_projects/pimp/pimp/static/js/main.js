/*
 * jQuery File Upload Plugin JS Example 6.7
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload();
    // $('.fileupload').each(function () {
    //     $(this).fileupload({
    //         dropZone: $(this)
    //     });
    // });

    // Enable iframe cross-domain access via redirect option:
    $('.fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(
            /\/[^\/]*$/,
            '/cors/result.html?%s'
        )
    );



    if (window.location.hostname === 'blueimp.github.com') {
        // Demo settings:
        $('.fileupload').fileupload('option', {
            url: '//jquery-file-upload.appspot.com/',
            maxFileSize: 5000000,
            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
            process: [
                {
                    action: 'load',
                    fileTypes: /^image\/(gif|jpeg|png)$/,
                    maxFileSize: 20000000 // 20MB
                },
                {
                    action: 'resize',
                    maxWidth: 1440,
                    maxHeight: 900
                },
                {
                    action: 'save'
                }
            ]
        });
        // Upload server status check for browsers with CORS support:
        if ($.support.cors) {
            $.ajax({
                url: '//jquery-file-upload.appspot.com/',
                type: 'HEAD'
            }).fail(function () {
                $('<span class="alert alert-error"/>')
                    .text('Upload server currently unavailable - ' +
                            new Date())
                    .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $('#fileupload').each(function () {
            var that = this;
            $.getJSON(this.action, function (result) {
                if (result && result.length) {
                    $(that).fileupload('option', 'done')
                        .call(that, null, {result: result});
                }
            });
        });

        // add by Yoann for file format restriction
        var url = document.URL;

        var totalSize = 0;

        $('#fileupload').fileupload({
            dropZone: $('#dropzone'),
            maxSizeOfFiles: 100000,
            getSizeOfFiles: function () {
                    return totalSize;
            },
            // add: function (e, data) {
            //     var jqXHR = data.submit()
            //         .success(function (result, textStatus, jqXHR) {
            //             alert("success");
            //         })
            //         .error(function (jqXHR, textStatus, errorThrown) {
            //             alert("error");
            //         })
            //         .complete(function (result, textStatus, jqXHR) {
            //             alert("complete");
            //         });
            // }
        });

        $('#fileupload').bind('fileuploadadd', function (e, data) {
            $.each(data.files, function (index, file) {
                console.log('Adding file: ' + file.name + ', ' + file.size);
                totalSize = totalSize + file.size;
                console.log('Total size: ' + totalSize);
            });
        });

        $('#fileupload').bind('fileuploadfailed', function (e, data) {
            $.each(data.files, function (index, file) {
                console.log('Removed file: ' + file.name + ', ' + file.size);
                totalSize = totalSize - file.size;
                console.log('Total size: ' + totalSize);
            });
        });
        //KMcL: Adding new file type to be accepted
        if (url.split("/")[url.split("/").length-2] == "projectfile"){
            console.log("hihi");
            $('#fileupload').fileupload('option', {
                acceptFileTypes: /(\.|\/)(mzxml|mzML|csv)$/i,
                sequentialUploads: true,
            });
        }

        //KMcL: Adding the fragment file to be accepted
        if (url.split("/")[url.split("/").length-2] == "fragmentfile"){
            console.log("fragupload");
            $('#fileupload').fileupload('option', {
                acceptFileTypes: /(\.|\/)(mzML)$/i,
                sequentialUploads: true,
            });
        }
        //KMcL: Adding mzML here too.
        if (url.split("/")[url.split("/").length-2] == "new"){
            console.log("hihi");
            $('#fileupload').fileupload('option', {
                acceptFileTypes: /(\.|\/)(mzxml|mzML)$/i,
                sequentialUploads: true,
            });
            // $('#fileupload').fileupload({maxChunkSize: 100000})
            //     .on('fileuploadchunksend', function (e, data) {
            //         alert("send");
            //     })
            //     .on('fileuploadchunkdone', function (e, data) {
            //         alert("done");
            //     })
            //     .on('fileuploadchunkfail', function (e, data) {
            //         alert("faile");
            //     })
            //     .on('fileuploadchunkalways', function (e, data) {
            //         alert("always");ß
            //     });
        }
        // end of add
    }

});
