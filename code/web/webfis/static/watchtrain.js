$(function(){
    $("#stop").button({
        icons: {primary: "ui-icon-check"},
        text: true
    }).click(function(){
        $.ajax({
            url: $SCRIPT_ROOT + '/endtrain/' + $TRAIN_ID,
            method: 'GET'
        });
    });
    
    var options = {
        lines: { show: true },
        points: { show: true },
        xaxis: { tickDecimals: 0, tickSize: 1 }
    }; 
    var data = [[]];
    var placeholder = $('#trainingplot');
    
    $.plot(placeholder, data, options);
    data = [[]];
    
    var iteration = 0;

    function fetchData(){
        function receive(d){
            if(d != "wait" && d != "end"){
                iteration += 1;
                data[0].push([iteration, d]);
                $("#error").empty().append(d);
                $.plot(placeholder, data, options);
            }
            if(d != "end"){
                setTimeout(fetchData, 200);
            }
            else{
                $("#desc").empty().append("Training finished");
            }
        }
        
        $.ajax({
            url: $SCRIPT_ROOT + '/gettrainerror/' + $TRAIN_ID,
            cache: false,
            method: 'GET',
            dataType: 'json',
            success: receive
        }); 
    }
    
    setTimeout(fetchData, 200);
});