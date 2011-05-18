var fis = {}

$(function() {
    $("#modeltabs").tabs();
    $("#defuzzmethod").change(function(){
        fis['defuzzmethod'] = $(this).val();
    });
    $("#funtype").change(function(){
        fis['funtype'] = $(this).val();
    });
    $("#save").button({
        icons: {primary: "ui-icon-disk"},
        text: true
    }).click(function(){
        saveFis();    
    });
    $("#train").button({
        icons: {primary: "ui-icon-lightbulb"},
        text: true
    });
    $("#evotrain").button({
        icons: {primary: "ui-icon-lightbulb"},
        text: true
    });
    $("#test").button({
        icons: {primary: "ui-icon-help"},
        text: true
    }).click(function(){
        $("#testdialog").dialog("open");
    });
    $("#addinput").button({
        icons: {primary: "ui-icon-plus"},
        text: true
    }).click(function(){
        addInput();
        redraw();
    });
    $("#addrule").button({
        icons: {primary: "ui-icon-plus"},
        text: true
    }).click(function(){
        addRule();
    });
    $( "#delinputdialog" ).dialog({
        autoOpen: false,
	resizable: false,
    	modal: true,
	buttons: {
            "Delete input": function() {
                fis['inputs'].splice($(this).data('num')-1, 1);
                redraw();
                $( this ).dialog( "close" );
            },
            Cancel: function() {
		$( this ).dialog( "close" );
	    }
	}
    });
    $( "#testdialog" ).dialog({
        autoOpen: false,
        resizible: false,
        modal: true,
        buttons: {
            "Test": function(){
                $.ajax({
                    type: 'GET',
                    url: $SCRIPT_ROOT + '/test/' + $MODEL_ID + '/' + $('#testselect').val(),
                    success: function(data) {
                        $('#testoutput').append('Square error: ' + data);
                    },
                    error: function() {
                        // add flash message
                        var flash = $('<div class=ui-widget />');
                        $('#main').append(flash);
                        var content = $('<div class="ui-state-error ui-corner-all" style="padding: .7em; margin-top: .7em" />');
                        flash.append(content);
                        content.append('<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em"></span>');
                        content.append('<strong>Error:</strong> Test failed');
                    }
                });
            },
            "OK": function() {
                $('#testoutput').empty();
                $( this ).dialog( "close" );
            }
        }
    });
    $( "#memfuncselect" ).change(function(){
        $("#memfuncparams").empty();
        if($(this).val() == "TriangleMemFunc"){
            $("#memfuncparams").append('a: <input type="text"><br/>');
            $("#memfuncparams").append('b: <input type="text"><br/>');
            $("#memfuncparams").append('c: <input type="text"><br/>');
        }
        if($(this).val() == "TrapezoidMemFunc"){
            $("#memfuncparams").append('a: <input type="text"><br/>');
            $("#memfuncparams").append('b: <input type="text"><br/>');
            $("#memfuncparams").append('c: <input type="text"><br/>');
            $("#memfuncparams").append('d: <input type="text"><br/>');
        }
        if($(this).val() == "BellMemFunc"){
            $("#memfuncparams").append('a: <input type="text"><br/>');
            $("#memfuncparams").append('b: <input type="text"><br/>');
            $("#memfuncparams").append('c: <input type="text"><br/>');
        }
    }).change();
    $( "#addmemfuncdialog" ).dialog({
        autoOpen: false,
	resizable: true,
	modal: true,
	buttons: {
            "Add membership function": function() {
                var params = new Array();
                $( "#memfuncparams input" ).each(function(){
                    params.push(parseFloat($(this).val()));
                });
                var mem_func = {
                    'type': $('#memfuncselect').val(),
                    'params': params
                }
                fis['inputs'][$(this).data('num')-1].push(mem_func);
                redraw();
                $( this ).dialog( "close" );
            },
            Cancel: function() {
		$( this ).dialog( "close" );
	    }
	}
    });
    $( "#addrulepartbutton" ).button({
        icons: {primary: "ui-icon-plus"},
        text: false
    });
    $('#ruleinputselect').change(function(){
        $('#rulememfuncselect').empty();
        for(var i=1; i<=fis['inputs'][parseInt($('#ruleinputselect').val())-1].length; i++){
            $('#rulememfuncselect').append('<option>'+i+'</option>');
        }
    });
    $('#addrulepartbutton').click(function(){
        $( '#addruledialog' ).data('inputs')
        .push(new Array(parseInt($('#ruleinputselect').val())-1, parseInt($('#rulememfuncselect').val())-1));
        var trule = "IF";
        $.each($( '#addruledialog' ).data('inputs'), function(i, input){
            if (i > 0){
                trule += " AND";
            }
            trule += " Input " + (input[0]+1) + " IS " + (input[1]+1);
        });
        $('#ruletext').empty().append(trule);
    });
    $( "#addruledialog" ).dialog({
        autoOpen: false,
	resizable: true,
	modal: true,
        width: 500,
	buttons: {
            "Add rule": function() {
                var params = new Array();
                $( "#ruleparams input" ).each(function(){
                    params.push(parseFloat($(this).val()));
                });
                var rule = {
                    'inputs': $(this).data('inputs'),
                    'params': params
                }
                fis['rules'].push(rule);
                redraw();
                $('#ruletext').empty()
                $( this ).dialog( "close" );
            },
            Cancel: function() {
                $('#ruletext').empty()
		$( this ).dialog( "close" );
	    }
	}
    });
    updateFis(redraw)
});

function updateFis(callback){
    $.getJSON($SCRIPT_ROOT + '/getfis/' + $MODEL_ID, function(data) {
        fis = data;
        callback();
    });
}

function saveFis(){
    $.ajax({
        type: 'POST',
        url: $SCRIPT_ROOT + '/updatefis/' + $MODEL_ID,
        data: {'fis': JSON.stringify(fis)},
        success: function() {
            // add flash message
            var flash = $('<div class=ui-widget />');
            $('#main').append(flash);
            var content = $('<div class="ui-state-highlight ui-corner-all" style="padding: .7em; margin-top: .7em" />');
            flash.append(content);
            content.append('<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em"></span>');
            content.append('Model succesfully saved');
        },
        error: function() {
            // add flash message
            var flash = $('<div class=ui-widget />');
            $('#main').append(flash);
            var content = $('<div class="ui-state-error ui-corner-all" style="padding: .7em; margin-top: .7em" />');
            flash.append(content);
            content.append('<span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em"></span>');
            content.append('<strong>Error:</strong> Save failed');
        }
    });
}

function addInput(){
    fis['inputs'].push(new Array());
}

function deleteInput(num){
    $( "#delinputdialog" ).data('num', num)
    .dialog('option', 'title', 'Delete input '+num)
    .dialog('open');
}

function addMemFunc(num){
    $("#addmemfuncdialog").data('num', num)
    .dialog('open');
}

function delMemFunc(i, j){
    fis['inputs'][i-1].splice(j, 1);
    redraw();
}

function addRule(){
    $('#ruleinputselect').empty();
    for(var i=1; i<=fis['inputs'].length; i++){
        $('#ruleinputselect').append('<option>'+i+'</option>');
    }
    
    $('#ruleparams').empty();
    $('#ruleparams').append('<tr/>');
    var j = 1;
    if(fis['funtype'] == 'lin'){
        j = fis['inputs'].length + 1;
    }
    for(var i=1; i<=j; i++){
        $('#ruleparams tr').append('<td><input type="text"></td>');
    }
    
    $('#ruleinputselect').change();
    $("#addruledialog").data('inputs', new Array()).dialog('open');
}

function delRule(num){
    fis['rules'].splice(num, 1);
    redraw();
}

function redraw(){
    //empty divs
    $('#inputs div').first().empty();
    $('#rules table').empty();
    
    //redraw fis
    $("#defuzzmethod").val(fis["defuzzmethod"])
    $("#funtype").val(fis["funtype"])
    $.each(fis["inputs"], function(i, input){
        
        var div = $('<div class="ui-corner-all ui-widget ui-widget-content" style="padding: .7em; margin-top: .7em"/>');
        $("#inputs div").first().append(div);
        div.append('<h3 style="display: inline">Input ' + (i+1) + '</h3>&nbsp;&nbsp;');
        var but = $('<span>Add membership function</span>').button({icons: {primary: "ui-icon-plus"}, text:true})
        .click(function(){
                addMemFunc(i);
        });
        div.append(but);
        but = $('<span>Delete input</span>').button({icons: {primary: "ui-icon-plus"}, text: true})
        .click(function(){
            deleteInput(i);
        });
        div.append('&nbsp;&nbsp;').append(but);
        
        var table = $('<table />');
        div.append(table);
        
        $.each(input, function(j, mem_func){
            var row = $('<tr />');
            table.append(row);
            row.append('<td>' + (j+1) + '</td><td>' + mem_func["type"] + "</td><td>" + mem_func["params"] + "</td>");
            var but = $('<span>Delete</span>').button({icons: {primary: "ui-icon-trash"}, text:false})
            .click(function(){
                delMemFunc(i, j);    
            });
            row.append(but);
        });
        
        i += 1;
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

        var row = $('<tr />');
        $("#rules table").append(row);
        row.append("<td>" + trule + "</td><td>" + rule["params"] + "</td>")
        var but = $('<span>Delete</span>').button({icons: {primary: "ui-icon-trash"}, text:false})
        .click(function(){
            delRule(i);
        });
        row.append(but);
    });
}