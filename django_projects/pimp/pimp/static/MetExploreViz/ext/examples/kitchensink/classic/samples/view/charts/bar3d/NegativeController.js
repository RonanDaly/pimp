Ext.define('KitchenSink.view.charts.bar3d.NegativeController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.bar-negative-3d',

    onDownload: function () {
        var chart = this.lookupReference('chart');

        if (Ext.os.is.Desktop) {
            chart.download({
                filename: '3D Bar Chart with Negative Values'
            });
        } else {
            chart.preview();
        }
    },

    onSeriesRender: function (sprite, config, data, index) {
        var isNegative = data.store.getAt(index).get('gaming') < 0;

        if (isNegative) {
            return {
                fillStyle: '#974144'
            };
        }
    }

});