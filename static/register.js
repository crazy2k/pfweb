var num = 1;

$(document).ready(function() {
    /* onclick event for the button that adds tabs */
    $('ul.idTabs li a.add_button').click(function() {
        num = num + 1;

        function refresh(num) {
            $('ul.idTabs').idTabs(num - 1);
        }

        $.get('pieces?func=progdata&num=' + num,
            function(data) {
                $("div#progdata_cont").append(data);

                $.get('pieces?func=progtab&num=' + num,
                    function(data) {
                        $("li#add_button_cont").before(data);
                        refresh(num);
                    });
            });

    });

    function val_from_sel(sel_selector) {
        var opt = $(sel_selector).children('option:selected');
        return opt.attr('value')
    }

    function num_from_sel(sel_selector) {
        return $(sel_selector).attr('name').split('/')[1];
    }

    /* onchange event for uni's select */
    $('select.uni_options').live('change', function() {
        var uni = val_from_sel(this);
        var num = num_from_sel(this);

        $.get('pieces?func=facslist&uni=' + uni,
            function(data) {
                var name = 'progdata/' + num + '/fac';
                var s = $('select.fac_options[name = ' + name + ']');
                s.html(data);
                s.trigger('change');
            });
    });

    /* onchange event for fac's select */
    $('select.fac_options').live('change', function() {
        var vals = val_from_sel(this).split('/');
        var uni = vals[0];
        var fac = vals[1];

        var num = num_from_sel(this);

        $.get('pieces?func=progslist&uni=' + uni + '&fac=' + fac,
            function(data) {
                var name = 'progdata/' + num + '/carr';
                var s = $('select.carr_options[name = ' + name + ']');
                s.html(data);
            });
    });
});

