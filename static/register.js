var num = 1;

$(document).ready(function() {
	/* onclick del boton que agrega tabs */
	$('ul.idTabs li a.add_button').click(function() {
		num = num + 1;

		function refresh(num) {
			$('ul.idTabs').idTabs(num - 1);
		}

		$.get('pieces?func=datoscarrera&num=' + num,
			function(data) {
				$("div#datoscarreras").append(data);

				$.get('pieces?func=tabcarrera&num=' + num,
					function(data) {
						$("li#add_button_holder").before(data);
						refresh(num);
					});
			});

	});

	function val_from_sel(sel_selector) {
		var opt = $(sel_selector).children('option:selected');
		return opt.attr('value')
	}

	function num_from_sel(sel_selector) {
		return $(sel_selector).attr('name').split('_')[1];
	}

	/* onchange para el select de universidad */
	$('select.uni_options').live('change', function() {
		var uni = val_from_sel(this);
		var num = num_from_sel(this);

		$.get('pieces?func=facslist&uni=' + uni,
			function(data) {
				var s = $('select.fac_options[name = fac_' + num + ']')
				s.html(data);
				s.trigger('change');
			});
	});

	/* onchange para el select de facultad */
	$('select.fac_options').live('change', function() {
		var vals = val_from_sel(this).split('/');
		var uni = vals[0];
		var fac = vals[1];

		var num = num_from_sel(this);

		$.get('pieces?func=carrslist&uni=' + uni + '&fac=' + fac,
			function(data) {
				var s = $('select.carr_options[name = carr_' + num + ']')
				s.html(data);
			});
	});
});

