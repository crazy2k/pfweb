var num = 1;

$(document).ready(function() {
	/* onclick del boton que agrega tabs */
	$('ul.idTabs li a.add_button').click(function() {
		num = num + 1;

		function refresh() {
			$('ul.idTabs').idTabs(0);
		}

		$.get('pieces?func=datoscarrera&num=' + num,
			function(data) {
				$("div#datoscarreras").append(data);
				refresh();
			});

		$.get('pieces?func=tabcarrera&num=' + num,
			function(data) {
				$("li#add_button_holder").before(data);
				refresh();
			});


	});
	/* onclick para las opciones del select de universidad */
	$('select.uni_options').live('change', function() {
		var sel = $(this);
		var opt = $(this).children('option:selected'); 

		var uni = opt.attr('value');
		var num = sel.attr('name').split('_')[1];

		$.get('pieces?func=facslist&uni=' + uni,
			function(data) {
				var s = $('select.fac_options[name = fac_' + num + ']')
				s.html(data);
			});


	});
});

