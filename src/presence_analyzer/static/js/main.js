google.load("visualization", "1", {packages:["corechart", 'timeline'], 'language': 'pl'});

function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}

(function($) {
    $(document).ready(function(){
        var loading = $('#loading'),
            user_avatar = $('img#user_avatar'),
            dropdown = $("#user_id");

        $.getJSON(urls.api_users, function(result) {
            $.each(result, function(item) {
                dropdown.append(
                    $("<option />").data('avatar', this.avatar).
                        val(this.user_id).text(this.name)
                );
            });
            dropdown.show();
            loading.hide();
        });

        dropdown.change(function(){
            var self = $(this),
                avatar_url = $('option:selected', self).data('avatar');

            user_avatar.hide();
            if(avatar_url){
                user_avatar.attr('src', avatar_url);
                user_avatar.show();
            }
        });
    });
})(jQuery);
