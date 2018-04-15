$(document).ready(function() {
    // set label values on lower bound of next range on input changes
    $('#attendance-range-1').on('input', function() {
        $('#attendance-range-1-val').text($(this).val());
    });

    $('#attendance-range-2').on('input', function() {
        $('#attendance-range-2-val').text($(this).val());
    });

    $('#attendance-range-3').on('input', function() {
        $('#attendance-range-3-val').text($(this).val());
    });
})