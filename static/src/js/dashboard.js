odoo.define('ptc_dashboard', function (require) 
{
	"use strict";

	var core = require('web.core');
	var Widget = require('web.Widget');
	var Model = require('web.Model');
	var session = require('web.session');
	var PlannerCommon = require('web.planner.common');
	var framework = require('web.framework');
	var webclient = require('web.web_client');
	var PlannerDialog = PlannerCommon.PlannerDialog;

	var QWeb = core.qweb;
	var _t = core._t;

	var Dashboard = Widget.extend({
		template: 'PTC_DashboardsMain',

		init: function(parent, data){
	        // this.all_dashboards = ['building','state','tax_payment','total_collection','expected_collection'];
	        this.all_dashboards = ['building','state','tax_payment'];
	        return this._super.apply(this, arguments);
	    },

	    start: function(){
	        return this.load(this.all_dashboards);
	    },

	    load: function(dashboards){

	        var self = this;
	        var loading_done = new $.Deferred();

	        session.rpc("/ptc_dashboard/data", {}).then(function (data) 
	        {

	            // Load each dashboard
	            var all_dashboards_defs = [];
	            _.each(dashboards, function(dashboard) {
	                var dashboard_def = self['load_' + dashboard](data);
	                if (dashboard_def) {
	                    all_dashboards_defs.push(dashboard_def);
	                }
	            });

	            // Resolve loading_done when all dashboards defs are resolved
	            $.when.apply($, all_dashboards_defs).then(function() {
	                loading_done.resolve();
	            });
	        });

	        return loading_done;
	    },

	    load_building: function(data){
	        // var build_paid = new PTC_Building_Paid(this, data.building).replace(this.$('.o_buildings_paid'));
	        var map_view = new PTC_Map_View(this, data.building).replace(this.$('.o_map_view'));
	    	// return build_paid,map_view
	    	return map_view
	    },

	    load_state: function(data){
	        var draft = new PTC_Building_Draft(this, data.state).replace(this.$('.o_buildings_draft'));
	        var stage = new PTC_Building_Stage(this, data.state).replace(this.$('.o_buildings_stage'));
	        var verify = new PTC_Building_Verify(this, data.state).replace(this.$('.o_buildings_verify'));
	        var round_graph = new PTC_Round_Graph(this, data.state).replace(this.$('.o_round_graph'));
	        var spline_graph = new PTC_Spline_Graph(this, data.state).replace(this.$('.o_spline_graph'));
	        return draft,stage,verify,round_graph,spline_graph;
	    },

	    load_tax_payment: function(data){
	        var bar_graph = new PTC_Bar_Graph(this, data.tax_payment).replace(this.$('.o_bar_graph'));
	        return bar_graph
	    },

	    // load_total_collection: function(data){
	    //     var ttl_collection_pt = new PTC_Total_Collection_PT(this, data.total_collection).replace(this.$('.o_ttl_collection_pt'));
	    //     var ttl_collection_rt = new PTC_Total_Collection_RT(this, data.total_collection).replace(this.$('.o_ttl_collection_rt'));
	    //     var ttl_collection_bbt = new PTC_Total_Collection_BBT(this, data.total_collection).replace(this.$('.o_ttl_collection_bbt'));
	    //     return ttl_collection_pt,ttl_collection_rt,ttl_collection_bbt
	    // },

	    // load_expected_collection: function(data){
	    //     var ex_collection_pt = new PTC_EX_Collection_PT(this, data.expected_collection).replace(this.$('.o_ex_collection_pt'));
	    //     var ex_collection_rt = new PTC_EX_Collection_RT(this, data.expected_collection).replace(this.$('.o_ex_collection_rt'));
	    //     var ex_collection_bbt = new PTC_EX_Collection_BBT(this, data.expected_collection).replace(this.$('.o_ex_collection_bbt'));
	    //     return ex_collection_pt,ex_collection_rt,ex_collection_bbt
	    // },
	});

	// var PTC_Building_Paid = Widget.extend({

	//     template: 'PTC_Building_Paid',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	var PTC_Building_Draft = Widget.extend({

	    template: 'PTC_Building_Draft',

	    events: {
	        'click .o_browse_draft': 'on_draft',
	    },

	    init: function(parent, data){
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	    },

	    on_draft: function() {
	    	this.do_action('property_tax_calculator.action_building_draft_context');
	    },
	});

	var PTC_Building_Stage = Widget.extend({

	    template: 'PTC_Building_Stage',

	    events: {
	        'click .o_browse_stage': 'on_stage',
	    },

	    init: function(parent, data){
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	    },

	    on_stage: function() {
	    	this.do_action('property_tax_calculator.action_building_staging_context');
	    },
	});

	var PTC_Building_Verify = Widget.extend({

	    template: 'PTC_Building_Verify',

	    events: {
	        'click .o_browse_verify': 'on_verify',
	    },

	    init: function(parent, data){
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	    },

	    on_verify: function() {
	    	this.do_action('property_tax_calculator.action_building_verify_context');
	    },
	});

	var PTC_Round_Graph = Widget.extend({

	    template: 'PTC_Round_Graph',

	    // events: {
	    //     'click #Draft': 'on_draft',
	    //     'click #Staging': 'on_stage',
	    //     'click #Verified': 'on_verify',
	    // },

	    init: function(parent, data){
	  
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);

	    	// return this.load();
	    },

	    // on_draft: function() {
	    // 	console.log('kkkkkkkkkkkkkkkkkkkkkkk')
	    // 	this.do_action('property_tax_calculator.action_building_draft_context');
	    // },

	    // on_stage: function() {
	    // 	this.do_action('property_tax_calculator.action_building_staging_context');
	    // },

	    // on_verify: function() {
	    // 	this.do_action('property_tax_calculator.action_building_verify_context');
	    // },

	    // load: function(){

	        // var self = this;
	        // var loading_done = new $.Deferred();
            
            // var complete_chart = [];

            // var loads = this.init_chart();

	        // //Load each dashboard
            // if (loads) {
                // complete_chart.push(loads);
            // }

            // // Resolve loading_done when all dashboards defs are resolved
            // $.when.apply($, complete_chart).then(function() {
                // loading_done.resolve();
            // });
            // return loading_done;
	    // },
	    // init_chart : function() {

	    	// c3.generate({
	    		// bindto: this.$('.pie-charto')[0],
			//     data: {
			//         columns: [
			//             ['data1', 10],
			//             ['data2', 10],
			//             ['data3', 10],
			//         ],

			//         type : 'pie',

			//         onclick: function (d, i) { console.log("onclick", d, i); },
			//         onmouseover: function (d, i) { console.log("onmouseover", d, i); },
			//         onmouseout: function (d, i) { console.log("onmouseout", d, i); }
			//     }
			// });

			// c3.generate(
			// {
			// 	bindto:this.$('.pie-charto')[0],
			// 	data:
			// 	{
			// 		columns:
			// 		[
			// 			["Desktops",5],
			// 			["Smart Phones",10],
			// 			["Mobiles",5],
			// 			["Tablets",5]
			// 		],
			// 		type:"pie"
			// 	},
			// 	color:
			// 	{
			// 		pattern:["#40a4f1","#ebeff2","#f5b225","#ec536c"]
			// 	},
			// 	pie:
			// 	{
			// 		label:
			// 		{
			// 			show:!1
			// 		}
			// 	}
			// });
	    // },
	});

	var PTC_Bar_Graph = Widget.extend({

	    template: 'PTC_Bar_Graph',

	    init: function(parent, data){
	  
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	    },
	});

	var PTC_Spline_Graph = Widget.extend({

	    template: 'PTC_Spline_Graph',

	    init: function(parent, data){
	  
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	    },
	});

	var PTC_Map_View = Widget.extend({

	    template: 'PTC_Map_View',

	    init: function(parent, data){
	  
	        this.data = data;
	        this.parent = parent;
	        return this._super.apply(this, arguments);
	    },

	    start: function() {
	        this._super.apply(this, arguments);
	        // return this.load();
	    },

	  //   load: function(){

	  //       var self = this;
	  //       var loading_done = new $.Deferred();
            
         //    var complete_chart = [];

         //    var loads = this.init_chart();

	        // //Load each dashboard
         //    if (loads) {
         //        complete_chart.push(loads);
         //    }

         //    // Resolve loading_done when all dashboards defs are resolved
         //    $.when.apply($, complete_chart).then(function() {
         //        loading_done.resolve();
         //    });
         //    return loading_done;
	    // },
	    // init_chart : function() {
	    	// console.log(this.$('.o_map')[0]);

	    	// var mymap = new L.Map(this.$('.o_map'), 
	     //    {
	     //      zoomControl: false,
	     //      center: [-6.81206, 39.28185],
	     //      zoom: 13
	     //    });

			// // ------------------------------------------------------

			// L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
	    //       attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
	    //     }).addTo(mymap);
	    // },
	});

	// var PTC_Total_Collection_PT = Widget.extend({

	//     template: 'PTC_Total_Collection_PT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	// var PTC_Total_Collection_RT = Widget.extend({

	//     template: 'PTC_Total_Collection_RT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	// var PTC_Total_Collection_BBT = Widget.extend({

	//     template: 'PTC_Total_Collection_BBT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	// var PTC_EX_Collection_PT = Widget.extend({

	//     template: 'PTC_EX_Collection_PT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	// var PTC_EX_Collection_RT = Widget.extend({

	//     template: 'PTC_EX_Collection_RT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	// var PTC_EX_Collection_BBT = Widget.extend({

	//     template: 'PTC_EX_Collection_BBT',

	//     init: function(parent, data){
	//         this.data = data;
	//         this.parent = parent;
	//         return this._super.apply(this, arguments);
	//     },

	//     start: function() {
	//         this._super.apply(this, arguments);
	//     },
	// });

	core.action_registry.add("property_tax_calculator.dashboard", Dashboard);

	return 
	{
	    Dashboard: Dashboard
	};

});