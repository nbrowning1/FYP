$(document).ready(function() {
    $('#feedback-submit').submit(function(e) {
        var fields = $(".feedback-form-answer:not(#id_feedback_other)").serializeArray();

        var anyEmpty = false;
        var lengthsInvalid = false;

        $.each(fields, function(i, field) {
            if (!field.value) {
                anyEmpty = true;
            }
            if (field.value.length > 1000) {
                lengthsInvalid = true;
            }
        });

        if (anyEmpty || lengthsInvalid) {
            e.preventDefault();
            var msg = "";
            if (anyEmpty) {
                msg = "Please fill in all form fields";
            }
            if (lengthsInvalid) {
                if (msg) {
                    msg += ", \n"
                }
                msg += "Feedback should be between 1 and 1000 characters";
            }
            $(".form-error").text(msg);
        }
    });
})