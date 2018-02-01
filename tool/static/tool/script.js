$(document).ready(function() {

    var uploadsCounter = 0;
    setup_file_uploads();
    setup_pagination();

    /* Sets up file uploads so that styled uploads contain filename
        when a file is uploaded.
        Also sets up onclick for adding new upload rows and the
        associated row-adding functionality. */
    function setup_file_uploads() {
        var uploadRowsContainer = document.getElementById("upload-rows-container");
        add_upload_row();

        $('#add-upload-row').click(function() {
            add_upload_row();
        });

        function add_upload_row() {
            var newFileUpload = document.getElementById("placeholder").cloneNode(true);
            newFileUpload.id = "";
            uploadRowsContainer.insertBefore(newFileUpload, uploadRowsContainer.firstChild);

            // file upload element
            var fileInput = document.getElementById("placeholder-file");
            fileInput.id = "file-" + uploadsCounter;
            fileInput.name = "upload-data-" + uploadsCounter;
            fileInput.nextElementSibling.htmlFor = "file-" + uploadsCounter;

            // filename text
            moduleTextEl = document.getElementById('filename-text');
            moduleTextEl.id = "";
            (function(_moduleTextEl){
                fileInput.addEventListener('change', function(e) {
                    var filenameSpanText;
                     if (e.target.files[0]) {
                        filenameSpanText = e.target.files[0].name;
                     } else {
                        filenameSpanText = 'Select a file';
                     }

                    _moduleTextEl.innerHTML = filenameSpanText;
                });
            })(moduleTextEl);

            // module select
            var moduleSelect = document.getElementById("placeholder-module");
            moduleSelect.id = "";
            moduleSelect.name = "module-" + uploadsCounter;
            $(moduleSelect).chosen({ width: '75%' });

            // delete button
            var deleteBtn = document.getElementById("placeholder-delete");
            deleteBtn.id = "";
            (function(uploadElement){
                $(deleteBtn).click(function() {
                    // delete actual element
                    $(uploadElement).remove();

                    // set existing uploads to have updated indices,
                    //  where bottom should be 0 index
                    var numUploadRows = $(".upload-row:not(#placeholder)").length;
                    $("input[id^='file-']").each(function (i, el) {
                        el.id = "file-" + (numUploadRows - i);
                    });
                    $("label[for^='file-']").each(function (i, el) {
                        el.htmlFor = "file-" + (numUploadRows - i);
                    });
                    $("select[id^='module-']").each(function (i, el) {
                        el.id = "module-" + (numUploadRows - i);
                    });
                    uploadsCounter--;
                });
            })(newFileUpload);

            uploadsCounter++;
        }
    }

    /* Sets up pagination for containers using objects stored in JS */
    function setup_pagination() {
        if ($('#modules-pagination').length) {
            $('#modules-pagination').pagination(
                build_pagination(modules, '#modules-tbl', module_row)
            )
        }

        if ($('#courses-pagination').length) {
            $('#courses-pagination').pagination(
                build_pagination(courses, '#courses-tbl', regular_row)
            )
        }

        if ($('#lecturers-pagination').length) {
            $('#lecturers-pagination').pagination(
                build_pagination(lecturers, '#lecturers-tbl', regular_row)
            )
        }

        if ($('#students-pagination').length) {
            $('#students-pagination').pagination(
                build_pagination(students, '#students-tbl', regular_row)
            )
        }

        if ($('#lectures-pagination').length) {
            $('#lectures-pagination').pagination(
                build_pagination(lectures, '#lectures-tbl', lecture_row)
            )
        }
    }

    function regular_row(item) {
        return '<td><a href="' + item.url + '">' + item.name + '</a></td>';
    }

    function module_row(item) {
        data = '<td><a href="' + item.url + '">' + item.code + '</a></td>';
        data += '<td><a href="' + item.url + '">' + item.crn + '</a></td>';
        return data;
    }

    function lecture_row(item) {
        data = '<td>' + item.module_code + '</td>';
        data += '<td><a href="' + item.url + '">' + item.session_id + '</a></td>';
        data += '<td>' + item.date + '</td>';
        return data;
    }

    function build_pagination(data_source, table_locator, tr_data_callback) {
        return {
            dataSource: data_source,
            pageSize: 5,
            showGoInput: true,
            showGoButton: true,
            callback: function(data, pagination) {
                var html = '';
                data.forEach(function(item, i) {
                    // build students data rows
                    if (i % 2 == 0) {
                        html += '<tr class="alt">';
                    } else {
                        html += '<tr>';
                    }
                    html += tr_data_callback(item);
                    html += '</tr>';
                })
                // replace table body with data rows
                $(table_locator + ' tbody').html(html);
            }
        }
    }
})