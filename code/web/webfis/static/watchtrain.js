$(function(){
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
                $.plot(placeholder, data, options);
            }
            if(d != "end"){
                setTimeout(fetchData, 200);
            }
        }
        
        $.ajax({
            url: $SCRIPT_ROOT + '/gettrainerror',
            cache: false,
            method: 'GET',
            dataType: 'json',
            success: receive
        }); 
    }
    
    setTimeout(fetchData, 200);
});