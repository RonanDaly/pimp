

$(document).ready(function() {
  /* Start JS for fragmentation_set.html */
  $('#annotation-set').DataTable({
    "paging": false,
    "info": false,
    "order": [[1, "desc"]], // order by Time Created
    "columnDefs": [{"targets": 5, "orderable": false}], // remove sort control on delete column
    "searching": false,
  });

  $('.MS1-peaks').DataTable({
    "columnDefs": [{"targets": 0, "type": "html-num"}],
    "order": [[0, "asc"]], // order by Identifier
    "paging": true,
    "lengthMenu": [[50, 100, -1], [50, 100, "All"]]
  });
  /* End JS for fragmentation_set.html */

  /* Start JS for my_fragmentation_sets.html */
  $('#fragmentation-set').DataTable({
    "order": [[1, "asc"]]
  });

  /* End JS for my_fragmentation_sets.html */
});
