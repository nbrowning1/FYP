$(document).ready(function() {
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