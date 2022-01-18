$(document).ready(function () {
  $('#plot-nav').click(function () {
    $('.sidebar-menu > li:nth-child(1) > a:nth-child(1)').trigger('click');

    $('#plot-nav').addClass('active');
    $('#table-nav').removeClass('active');
    $('#species-nav').removeClass('active');
  });

  $('#table-nav').click(function () {
    $('.sidebar-menu > li:nth-child(2) > a:nth-child(1)').trigger('click');

    $('#plot-nav').removeClass('active');
    $('#table-nav').addClass('active');
    $('#species-nav').removeClass('active');
  });

  $('#species-nav').click(function () {
    $('.sidebar-menu > li:nth-child(3) > a:nth-child(1)').trigger('click');

    $('#plot-nav').removeClass('active');
    $('#table-nav').removeClass('active');
    $('#species-nav').addClass('active');
  });

  if (false) {
    var oldJQueryEventTrigger = jQuery.event.trigger;
    jQuery.event.trigger = function( event, data, elem, onlyHandlers ) {
      console.log( event, data, elem, onlyHandlers );
      oldJQueryEventTrigger( event, data, elem, onlyHandlers );
    }
  }

  $("#sidebarCollapsed").change(function() {
    var collapsed = $("#sidebarCollapsed").attr("data-collapsed");
    var is_mobile = false;

    if( $('#mobileTest').css('display')=='none') {
        is_mobile = true;
    }

    if (is_mobile == true) {
      $("#mobile_legend").parent().show();
      $("#legend").parent().hide();
      $("#epi_plot").parent().hide();
    }
    else {
      $("#mobile_legend").parent().hide();
      $("#legend").parent().show();
      $("#epi_plot").parent().show();
    }

  })
});
