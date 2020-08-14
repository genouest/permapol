$(function () {

  /* Functions */

  var loadForm = function () {
    $.ajax({
      url: "/groups/create",
      type: 'get',
      beforeSend: function () {
        console.log("test2")
        $("#modal-group").modal("show");
      },
      success: function (data) {
        $("#modal-group .modal-content").html(data);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: "/groups/create",
      data: form.serialize(),
      type: form.attr("method"),
      success: function (data) {
        if (data.status == 'ok') {
            $('#Modal').modal('hide');
            window.location = data.redirect;
        } else {
            var obj = JSON.parse(data);
            for (var key in obj) {
              if (obj.hasOwnProperty(key)) {
                var value = obj[key];
              }
            }
            $('.help-block').remove()
            $('<p class="help-block" style="color:red">' + value + '</p>')
                .insertAfter('#' + key);
            $('.form-group').addClass('has-error')
        }
      }
    });
    return false;
  };

  /* Binding */
    $("#admin_groups").on("click", ".js-create", loadForm);
    $("#modal-group").on("submit", ".js-form", saveForm);
});
