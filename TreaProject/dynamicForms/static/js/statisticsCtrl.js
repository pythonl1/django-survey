'use strict';

(function () {
	
    var app = angular.module('dynamicFormsFramework');
    
    /*
     * This controller handles the logic to create, edit and save a form.
     */    
    app.controller('statisticsCtrl', function ($scope, $http, $location, $window, $filter) {
    	
        var separator = '/';
        var stat = this;
    	stat.formId = ($location.search()).form;
        stat.versionNumber = ($location.search()).ver;
        stat.json = "";
        $scope.templates = {
            'number': '/dynamicForms/field_statistic/number/',
            'list': '/dynamicForms/field_statistic/list/',
        }
        stat.config = {
            title: '',
            tooltips: true,
            labels: false,
            mouseover: function() {},
            mouseout: function() {},
            click: function() {},
            legend: {
                display: true,
                //could be 'left, right'
                position: 'right'
            }
        };

        stat.data = {
            series: [],
            data: [{
              x: "",
              y: []
              
            }, {
              x: "",
              y: []
            }, {
              x: "",
              y: []
            }, {
              x: "",
              y: []
            },{
              x: "",
              y: []
            }]
          };
        
        stat.values ={
        };
        
        stat.getF= function(){
        
        $http.get('/dynamicForms/statistics/'+stat.formId+'/'+stat.versionNumber+'/')
        
                .success(function(data){
                    stat.json = JSON.parse(JSON.stringify(data));
                    //console.log(stat.json);
                    for(var field in stat.json){
                        var field_id = $.extend({}, stat.json[field]);
                        if (field_id.field_type=='number'){
                            var conf = angular.copy(stat.config);
                            conf.title = field_id.field_text;
                            var d = angular.copy(stat.data);
                            for(var i=0; i<5; i++){
                                d.data[i].x=field_id.quintilesX[i];
                                d.data[i].y=[field_id.quintilesY[i]];
                            
                            }
                            stat.values[field] = {
                                'id': field,
                                'chart': 'pie',
                                'field_type': 'number',  
                                'conf': conf,
                                'data': d,
                                'm' : field_id.mean,
                                'mt' : field_id.total_mean,
                                'sd' : field_id.standard_deviation,
                                'sdt' : field_id.total_standard_deviation,
                                'tf' : field_id.total_filled,
                                'tnf': field_id.total_not_filled
                            }
                        }
                                        
                    }
                     //console.log(stat.values);
                     //console.log(stat.values['id_field'].conf);
                })
                .error(function(data, status, headers, config){
                    alert('error loading statistics: ' + status);
                });
        
        };
     
        stat.getF();
       // console.log(stat.values);

       $scope.createPDF = function(){
                            // var doc = new jsPDF();
                            // doc.text(20, 20, 'Hello world!');
                            // doc.text(20, 30, 'This is client-side Javascript, pumping out a PDF.');
                            // doc.addPage('a6','l');
                            // doc.text(20, 20, 'Do you like that?');
                            // doc.save();
                           
                            var data = [],fontSize = 12, height = 0,doc;
                            doc = new jsPDF('p', 'pt', 'a4', true);
                            doc.setFont("courier", "normal");
                            doc.setFontSize(fontSize);
                            for (var insert = 0; insert <= 20; insert++) {
                                data.push({
                                    "name" : "jspdf plugin",
                                    "version" : insert,
                                    "author" : "Guillermo Kuster",
                                    "Designation" : "AngularJs Developer"
                                });
                            }
                            height = doc.drawTable(data, {xstart:10,ystart:10,tablestart:70,marginleft:50});      
                            doc.save("statistics.pdf");
                         
                           }
        
    $scope.chart_types = [
        'pie',
        'bar',
    ];    

});
})();
