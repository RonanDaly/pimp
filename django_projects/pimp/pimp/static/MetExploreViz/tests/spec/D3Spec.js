// Test creation of svg 
describe('Test svg after refresh network', function() {
    var c;
    
    beforeEach(function() {
        MetExploreViz.onloadMetExploreViz(function(){
            c = metExploreViz.GraphNetwork.delayedInitialisation();
            c.render();
        });
    });

    afterEach(function() {
        d3.selectAll('svg').remove();
    });

    it('should be created', function() {
        console.log(getSvg());
        expect(getSvg()).not.toBeNull();
    });

    function getSvg() {
        return d3.select('svg');
    }    
});

// ToDo 
// Number of created nodes 
// Number of created links 
// Number of reversible links 
// Number of nodes for each compartments