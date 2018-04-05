$(document).ready(function() {

    var uploadsCounter = 0;
    var csrf_token = get_csrf_token();
    setup_ajax(csrf_token);
    setup_pagination();
    setup_file_uploads();

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

    /* Sets up file uploads so that styled uploads contain filename
        when a file is uploaded.
        Also sets up onclick for adding new upload rows and the
        associated row-adding functionality. */
    function setup_file_uploads() {
        var uploadRowsContainer = document.getElementById("upload-rows-container");
        if (!uploadRowsContainer) {
            return;
        }
        add_upload_row();
        setup_submit();

        // allow adding new upload rows on add row click
        $('#add-upload-row').click(function() {
            add_upload_row();
        });

        function setup_submit() {
            $('#attendance-upload-form').submit(function(e) {
                var postUrl = $(this).attr('action');
                var formData = new FormData($(this).get(0));
                // need to manually append files data to form data
                $("input[id^='file-']").each(function (i, el) {
                    if (el.files[0]) {
                        formData.append('file-' + i, el.files[0]);
                    }
                });

                e.preventDefault();

                /* show loading spinner until ajax response is returned
                    - file processing can take a while */
                var uploadError = $("#upload-error-message-text")
                var loadingSpinner = $("#loading-spinner-container");
                var uploadResults = $("#upload-results");
                uploadError.text('')
                loadingSpinner.slideDown(function() {
                    // scroll spinner into view to show user that request is being processed
                    loadingSpinner[0].scrollIntoView(true);
                });
                uploadResults.hide();

                $.ajax({
                    context: this,
                    url: postUrl,
                    type: 'POST',
                    data: formData,
                    // required for file upload
                    processData: false,
                    contentType: false,
                    success: function(data) {
                        if (data.failure) {
                            uploadError.text(data.failure);
                        } else {
                            uploadResults.slideDown("fast", function() {
                                // scroll results into view
                                uploadResults[0].scrollIntoView(true);
                            });
                            uploadResults.html(data);
                        }
                    },
                    error: function() {
                        console.log("Fatal error occurred");
                    }
                })
                // hide spinner again
                .always(function() {
                    loadingSpinner.hide();
                });
            });
        }

        function add_upload_row() {
            // clone placeholder upload and remove id
            var newFileUpload = document.getElementById("placeholder").cloneNode(true);
            newFileUpload.id = "";
            // add to top of existing uploads
            uploadRowsContainer.insertBefore(newFileUpload, uploadRowsContainer.firstChild);

            // file upload element - change id, name, label to indicate index of new upload
            var fileInput = document.getElementById("placeholder-file");
            fileInput.id = "file-" + uploadsCounter;
            fileInput.name = "upload-data-" + uploadsCounter;
            fileInput.nextElementSibling.htmlFor = "file-" + uploadsCounter;

            // filename text (appears after uploading)
            moduleTextEl = document.getElementById('filename-text');
            moduleTextEl.id = "";
            (function(_moduleTextEl){
                // on file upload, change text to indicate file that was uploaded
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
            moduleSelect.id = "module-" + uploadsCounter;
            moduleSelect.name = "module-" + uploadsCounter;
            $(moduleSelect).chosen({ width: '75%' });

            // delete button
            var deleteBtn = document.getElementById("placeholder-delete");
            deleteBtn.id = "";
            (function(uploadElement){
                $(deleteBtn).click(function() {
                    // delete actual element
                    $(uploadElement).remove();

                    // set existing uploads to have updated indices after removal,
                    //  where bottom element should be 0 index
                    var numUploadRows = $(".upload-row:not(#placeholder)").length;
                    $("input[id^='file-']").each(function (i, el) {
                        el.id = "file-" + (numUploadRows - (i+1));
                        el.name = "upload-data-" + (numUploadRows - (i+1));
                    });
                    $("label[for^='file-']").each(function (i, el) {
                        el.htmlFor = "file-" + (numUploadRows - (i+1));
                    });
                    $("select[id^='module-']").each(function (i, el) {
                        el.id = "module-" + (numUploadRows - (i+1));
                        el.name = "module-" + (numUploadRows - (i+1));
                    });
                    uploadsCounter--;
                });
            })(newFileUpload);

            uploadsCounter++;
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

    // lifted from https://docs.djangoproject.com/en/dev/ref/csrf/
    function get_csrf_token() {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var name = 'csrftoken';
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function setup_ajax(csrftoken) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
    }
})