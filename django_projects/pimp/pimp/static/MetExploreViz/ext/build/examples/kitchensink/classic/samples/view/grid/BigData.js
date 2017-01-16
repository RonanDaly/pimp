/**
 * This is an example of using the Ext JS grid to show very large datasets
 * without overloading the DOM. It also uses locking columns, and incorporates the
 * GroupSummary feature. Filtering is enabled on certain columns using the FilterFeature.
 *
 * As an illustration of the ability of grid columns to act as containers, the Title
 * column has a filter text field built in which filters as you type.
 *
 * The grid is editable using the RowEditing plugin.
 *
 * The `multiColumnSort` config is used to allow multiple columns to have sorters.
 *
 * It is also possible to export the grid data to Excel. This feature is available in Ext JS Premium.
 */
Ext.define('KitchenSink.view.grid.BigData', {
    extend: 'Ext.grid.Panel',
    requires: [
        'Ext.grid.filters.Filters',
        'Ext.grid.plugin.Exporter'
    ],
    xtype: 'big-data-grid',
    store: 'BigData',
    columnLines: true,
    height: 400,
    width: 910,
    title: 'Editable Big Data Grid',
    multiColumnSort: true,

    // We do not need automatic height synching.
    // The Grouping plugin renders the same DOM into each side to keep heights the same,
    // The normal side is visibility:hidden.
    // And the RowExpander handles this itself when a row is expanded, or when an expanded
    // row is scrolled back into the rendered block.
    syncRowHeight: false,

    //<example>
    exampleTitle: 'Editable Big Data Grid',
    otherContent: [{
        type: 'Controller',
        path: 'classic/samples/view/grid/BigDataController.js'
    },{
        type: 'Store',
        path: 'classic/samples/store/BigData.js'
    },{
        type: 'Model',
        path: 'classic/samples/model/grid/Employee.js'
    }],
    exampleDescription: [
        '<p>This example uses locking columns, and incorporates the GroupSummary feature.</p>' +
        '<p>Filtering is enabled on certain columns using the FilterFeature UX.</p>' +
        '<p>As an illustration of the ability of grid columns to act as containers, the ' +
        'Title column has a filter text field built in which filters as you type.</p>' +
        '<p>The grid is editable using the RowEditing plugin.</p>',
        '<p>The <code>multiColumnSort</code> config is used to allow multiple columns to have sorters.</p>' +
        '<p>The full name column uses a custom sorter which sorts on the surname.</p>'
    ].join(''),
    //</example>
    controller: 'bigdata',

    features: [{
        ftype : 'groupingsummary',
        groupHeaderTpl : '{name}',
        hideGroupedHeader : false,
        enableGroupingMenu : false
    }, {
        ftype: 'summary',
        dock: 'bottom'
    }],

    selModel: {
        type: 'checkboxmodel',
        checkOnly: true
    },
    
    listeners: {
        headermenucreate: 'onHeaderMenuCreate'
    },

    columns:[{
        xtype: 'rownumberer',
        width: 40,
        sortable: false,
        locked: true
    }, {
        text: 'Id',
        sortable: true,
        dataIndex: 'employeeNo',
        groupable: false,
        width: 80,
        locked: true,
        editRenderer: 'bold'
    }, {
        text: 'Name (Filter)',
        sortable: true,
        dataIndex: 'name',
        groupable: false,
        width: 140,
        layout: 'hbox',
        locked: true,
        renderer: 'concatNames',
        editor: {
            xtype: 'textfield'
        },
        // Sort prioritizing surname over forename as would be expected.
        sorter: function(rec1, rec2) {
            var rec1Name = rec1.get('surname') + rec1.get('forename'),
                rec2Name = rec2.get('surname') + rec2.get('forename');

            if (rec1Name > rec2Name) {
                return 1;
            }
            if (rec1Name < rec2Name) {
                return -1;
            }
            return 0;
        },
        items    : {
            xtype: 'textfield',
            reference: 'nameFilterField',  // So that the Controller can access it easily
            flex : 1,
            margin: 2,
            enableKeyEvents: true,
            listeners: {
                keyup: 'onNameFilterKeyup',
                buffer: 500
            }
        }
    }, {
        text: 'Rating',
        width: 100,
        sortable: true,
        dataIndex: 'rating',
        groupable: false,
        xtype: 'widgetcolumn',
        widget: {
            xtype: 'sparklineline'
        }
    }, {
        text: 'Date of birth',
        dataIndex: 'dob',
        xtype: 'datecolumn',
        groupable: false,
        width: 115,
        filter: {

        },
        editor: {
            xtype: 'datefield'
        }
    }, {
        text: 'Join date',
        dataIndex: 'joinDate',
        xtype: 'datecolumn',
        groupable: false,
        width: 120,
        filter: {

        },
        editor: {
            xtype: 'datefield'
        }
    }, {
        text: 'Notice<br>period',
        dataIndex: 'noticePeriod',
        groupable: false,
        width: 115,
        filter: {
            type: 'list'
        },
        editor: {
            xtype: 'combobox',
            initComponent: function() {
                this.store = this.column.up('tablepanel').store.collect(this.column.dataIndex, false, true);
                Ext.form.field.ComboBox.prototype.initComponent.apply(this, arguments);
            }
        }
    }, {
        text: 'Email address',
        dataIndex: 'email',
        width: 200,
        groupable: false,
        renderer: function(v) {
            return '<a href="mailto:' + v + '">' + v + '</a>';
        },
        editor: {
            xtype: 'textfield'
        },
        filter: {

        }
    }, {
        text: 'Department',
        dataIndex: 'department',
        hidden: true,
        hideable: false,
        filter: {
            type: 'list'
        }
    }, {
        text: 'Absences',
        columns: [{
            text: 'Illness',
            dataIndex: 'sickDays',
            width: 100,
            groupable: false,
            summaryType: 'sum',
            summaryFormatter: 'number("0")',
            filter: {

            },
            editor: {
                xtype: 'numberfield',
                decimalPrecision: 0
            }
        }, {
            text: 'Holidays',
            dataIndex: 'holidayDays',
            // Size column to title text
            width: null,
            groupable: false,
            summaryType: 'sum',
            summaryFormatter: 'number("0")',
            filter: {

            },
            editor: {
                xtype: 'numberfield',
                decimalPrecision: 0
            }
        }, {
            text: 'Holiday Allowance',
            dataIndex: 'holidayAllowance',
            // Size column to title text
            width: null,
            groupable: false,
            filter: {

            },
            editor: {
                xtype: 'numberfield',
                decimalPrecision: 0
            }
        }]
    }, {
        text: 'Salary',
        width: 155,
        sortable: true,
        dataIndex: 'salary',
        align: 'right',
        formatter: 'usMoney',
        groupable: false,
        summaryType: 'average',
        summaryFormatter: 'usMoney',
        filter: {

        },
        editor: {
            xtype: 'numberfield',
            decimalPrecision: 2
        }
    }],

    viewConfig: {
        stripeRows: true
    },
    
    header: {
        itemPosition: 1, // after title before collapse tool
        items: [{
            ui: 'default-toolbar',
            xtype: 'button',
            text: 'Export to Excel',
            handler: 'exportToExcel'
        }]
    },

    plugins: [{
        ptype: 'gridfilters'
    }, {
        ptype: 'rowexpander',

        // dblclick invokes the row editor
        expandOnDblClick: false,
        rowBodyTpl: '<img src="{avatar}" height="100px" style="float:left;margin:0 10px 5px 0"><b>{name}<br></b>{dob:date}'
    },{
        ptype: 'gridexporter'
    }]
});
