describe("EditorCtrl Testing Pages", function() {
    
    beforeEach(angular.mock.module('dynamicFormsFrameworkAdmin'));
    
    it("Field Types constant successfully loaded.", inject(function( _$httpBackend_,$controller,$rootScope) {
        var scope = $rootScope.$new();
        var $httpBackend = _$httpBackend_;
        var ctrl = $controller('EditorCtrl', {$scope: scope});     
        expect(ctrl.FieldTypes).not.toBe(null);
        expect(ctrl.FieldTypes).toBeDefined();
    }));
    
    it("Adding Pages.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});
        expect(ctrl.pages[0]).not.toBeNull();
        ctrl.addPage();
        expect(ctrl.pages[1]).toBeDefined();
        expect(ctrl.pages[1]).not.toBeNull();
        expect(ctrl.pages[1]!=ctrl.pages[0]).toBe(true);
        expect(ctrl.pages.length).toBe(2);
    }));

    it("Delete Pages.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});     
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        expect(ctrl.pages.length).toBe(7); /*Page already added from last it*/
        ctrl.deletePage(0);
        expect(ctrl.pages.length).toBe(6);     
    }));

    it("Select Page.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});     
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.addPage();
        ctrl.selectPage(4);     
        expect(ctrl.selectedPage).toBe(ctrl.pages[4]);
    }));
    
});

describe("EditorCtrl Testing Fields", function() {
    
    beforeEach(angular.mock.module('dynamicFormsFrameworkAdmin'));
    
    xit("Add Fields to Some Page.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});
        ctrl.addPage();
        ctrl.addPage();
        expect(ctrl.pages.length).toBe(3);    
        ctrl.selectPage(0);  
        ctrl.addField(ctrl.FieldTypes[0]);
        ctrl.addField(ctrl.FieldTypes[0]);
        ctrl.addField(ctrl.FieldTypes[0]);
        expect(ctrl.pages[0].fields[0]).not.toBe(null);
        expect(ctrl.pages[0].fields[0]).toBeDefined();
        expect(ctrl.pages[0].fields.length).toBe(3);
    }));
    
    xit("Delete Fields in Some Page.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});
        ctrl.addPage();
        ctrl.addPage();
        expect(ctrl.pages.length).toBe(3);
        ctrl.selectPage(0);  
        ctrl.addField(ctrl.FieldTypes[0]);
        ctrl.addField(ctrl.FieldTypes[0]);
        ctrl.addField(ctrl.FieldTypes[0]);
        expect(ctrl.pages[0].fields.length).toBe(3);
        ctrl.deleteField(0,1);
        expect(ctrl.pages[0].fields.length).toBe(2);      
    }));
    
    xit("Add Options to Some Field in a page.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});
        ctrl.addPage();
        ctrl.addPage();
        expect(ctrl.pages.length).toBe(3);
        ctrl.selectPage(0);  
        ctrl.addField("check_box");
        ctrl.addField("check_box");
        ctrl.addField("check_box");      
        ctrl.selectField(0,0);
        ctrl.addOption();
        alert(ctrl.pages[0].fields[0].options);
        expect(ctrl.pages[0].fields[0].options.length).toBe(1);
        ctrl.selectField(0,2);
        ctrl.addOption();
        alert(ctrl.pages[0].fields[2].options);
        expect(ctrl.pages[0].fields[2].options.length).toBe(1);    
    }));
    
    xit("Delete Options to Some Field in a page.", inject(function($controller,$rootScope) {
        var scope = $rootScope.$new();
        var ctrl = $controller('EditorCtrl', {$scope: scope});
        ctrl.selectPage(0);  
        ctrl.addField("check_box");
        ctrl.addField("check_box");
        ctrl.addField("check_box");      
        ctrl.selectField(0,2);
        ctrl.addOption();
        expect(ctrl.pages[0].fields[2].options.length).toBe(1);
        ctrl.deleteOption(0);
        expect(ctrl.pages[0].fields[2].options.length).toBe(0);
    }));

});

describe("EditorCtrl testing logic", function() {
    
    beforeEach(angular.mock.module('dynamicFormsFrameworkAdmin'));
    beforeEach(inject(function ($rootScope, $controller, _$location_, _$httpBackend_) {
        $location = _$location_;
        scope = $rootScope.$new();
        $httpBackend = _$httpBackend_;
        createController = function() {
            return $controller('EditorCtrl', {
                '$scope': scope
            });
        };
    }));

    it("Adding a logic condition to a field", inject(function($controller,$rootScope) {
        var ctrl = createController();
        scope.pages = getFakeForm().pages;
        scope.logic = getFakeForm().logic;
        ctrl.configLogicField();
        expect(ctrl.logicField.conditions.length).toBe(0);
        ctrl.addNewLogicCondition();
        expect(ctrl.logicField.conditions.length).toBe(1);
    }));
  
    getFakeForm = function(){
        var pages = [
            {"fields":[{"dependencies":{"fields":[],"pages":[]},"text":"text","field_type":"TextField","tooltip":"","answer":[],"field_id":1,"required":false,"validations":{"max_len_text":255}}],"subTitle":""},
            {"fields":[{"dependencies":{"fields":[],"pages":[]},"text":"number","field_type":"NumberField","tooltip":"","answer":[],"field_id":3,"required":false,"validations":{"max_number":null,"min_number":null}}],"subTitle":""},
            {"fields":[{"dependencies":{"fields":[],"pages":[]},"text":"textArea","field_type":"TextAreaField","tooltip":"","answer":[],"field_id":4,"required":false,"validations":{"max_len_text":400}}],"subTitle":""}];

        var logic = {
            "fields": {},
            "pages": {}
        };

        var form = {};
        form.pages = pages;
        form.logic = logic;

        return form;
    }; 
});
