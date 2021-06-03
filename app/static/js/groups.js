$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      beforeSend: function () {
        $("#modal-group").modal("show");
      },
      success: function (data) {
        $("#modal-group .modal-content").html(data);
      }
    });
  };

  var saveForm = function (event) {
    var form = $(this);

    // Disable the submit button
    var button = $(event.target).eq(0).find('#submit')
    var old_button_name = button.html()
    button.prop("disabled", true);
    button.html(
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ' + old_button_name
    );

    $.ajax({
      url: form.attr("data-url"),
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
            button.html(old_button_name);
            button.prop("disabled", false);
        }
      },
      error: function (xhr, ajaxOptions, thrownError) {
        $('.help-block').remove()
        $('<p class="help-block" style="color:red">Error from server</p>')
            .insertAfter('#group_name');
        $('.form-group').addClass('has-error')
        button.html(old_button_name);
        button.prop("disabled", false);
      }
    });
    return false;
  };

  /* Binding */
  $("#admin_groups").on("click", ".js-create", loadForm);
  $("#members").on("click", ".js-create", loadForm);
  $("#members").on("click", ".js-delete", loadForm);
  $("#organisms").on("click", ".js-form", loadForm);
  $("#modal-group").on("submit", ".js-form", saveForm);

  // Show the correct tag if passed by url
  var hash = window.location.hash;
  hash && $('div.list-group a[href="' + hash + '"]').tab('show');
});
