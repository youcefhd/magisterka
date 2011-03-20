$(function() {
    $('.addbutton').each(function(){
        $(this).button({
            icons: {primary: "ui-icon-plusthick"},
            text: false
        });
    })
    $('.delbutton').each(function(){
        $(this).button({
            icons: {primary: "ui-icon-trash"},
            text: false
        });
    });
});

