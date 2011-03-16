var fis = {}

$(function() {
    $("#modeltabs").tabs();
    $("#save").button({
        icons: {primary: "ui-icon-disk"},
        text: true
    });
    $("#train").button({
        icons: {primary: "ui-icon-lightbulb"},
        text: true
    });
    updateFis(redraw)
});

function updateFis(callback){
    $.getJSON($SCRIPT_ROOT + '/getfis/' + $MODEL_ID, function(data) {
        fis = data;
        callback();
    });
}

function redraw(){
    $("#defuzzmethod").val(fis["defuzzmethod"])
    $("#funtype").val(fis["funtype"])
    $.each(fis["inputs"], function(i, input){
        var div = $('<div class="ui-corner-all ui-widget ui-widget-content" style="padding: .7em; margin: .3em"/>');
        $("#inputs").append(div);
        div.append("<h3>Input " + (i+1) + "</h3>");
        var table = $('<table />');
        div.append(table);
        i += 1;
        $.each(input, function(i, mem_func){
            table.append('<tr><td>' + (i+1) + '</td><td>' + mem_func["type"] + "</td><td>" + mem_func["params"] + "</td></tr>");
        });
    });
    $.each(fis['rules'], function(i, rule){
        var trule = "IF";
        $.each(rule["inputs"], function(i, input){
            if (i > 0){
                trule += " AND";
            }
            trule += " Input " + (input[0]+1) + " IS " + (input[1]+1);
        });
        trule += " THAN Output params are:"
        $("#rules table").append("<tr><td>" + trule + "</td><td>" + rule["params"] + "</td></tr>");
    });
}