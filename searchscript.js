// Initialize Isotope
// =============================================
var filtr = "";

function startCode() {
	var $container = $('#container').isotope({
		itemSelector: '.element-item',
		layoutMode: 'fitRows',
		getSortData: {
			name: '[data-isotope-sort-name]'
		}
	});
	
	filterItemHandler();
  sortItemHandler();
  searchItemHandler();
};

// FILTER HANDLER
// =============================================
function filterItemHandler(){
  var $container = $('#container').isotope();
	
	$('#filters').on( 'click', 'button', function() {
    filtr = $( this ).attr('data-filter');
    
		$container.isotope({ filter: filtr });
    console.info( 'FILTER: ', filtr );
  });
}


// SEARCH HANDLER
// =============================================
function searchItemHandler(){
  var $container = $('#container').isotope();
	var qsRegex;
  
  var $quicksearch = $('#quicksearch').keyup( debounce( function() {
    qsRegex = new RegExp( $quicksearch.val(), 'gi' );
    $container.isotope({
      filter: function() {
        var $this = $(this);
        var searchResult = qsRegex ? $this.text().match( qsRegex ) : true;
        var buttonResult = filtr ? $this.is( filtr ) : true;
        return searchResult && buttonResult;
      }
    });
    // console.info( 'SEARCH: ', $grid.isotope() );
  }, 200 ) );
}

	// debounce so filtering doesn't happen every millisecond
	function debounce( fn, threshold ) {
		var timeout;
		return function debounced() {
			if ( timeout ) {
				clearTimeout( timeout );
			}
			function delayed() {
				fn();
				timeout = null;
			}
			timeout = setTimeout( delayed, threshold || 100 );
		}
	}


// SORT HANDLER
// =============================================
function sortItemHandler(){
	var $container = $('#container').isotope();
	
	$('#quicksort').on( 'click', function() {
		var sortValue = $(this).attr('data-sort-value');
		
		$container.isotope({ sortBy: 'name' });
		
    console.info( 'SORT: ', sortValue );
  });
}


// =============================================
// =============================================
$(document).ready(function(){
 
  startCode();
});


// Set Hidden Classes for Isotope Items
// =============================================
var itemReveal = Isotope.Item.prototype.reveal;
Isotope.Item.prototype.reveal = function() {
  itemReveal.apply( this, arguments );
  $( this.element ).removeClass('isotope-hidden');
};

var itemHide = Isotope.Item.prototype.hide;
Isotope.Item.prototype.hide = function() {
  itemHide.apply( this, arguments );
  $( this.element ).addClass('isotope-hidden');
};

// Button Handler
// =============================================
$('.button-group').each( function( i, buttonGroup ) {
  var $buttonGroup = $( buttonGroup );
  $buttonGroup.on( 'click', 'button', function() {
    $buttonGroup.find('.is-checked').removeClass('is-checked');
    $( this ).addClass('is-checked');
    $('#quicksearch').val('');
  });
});