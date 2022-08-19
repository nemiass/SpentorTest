(function(){

    /**
     * Easy selector helper function
     */
    const select = (el, all = false) => {
        el = el.trim()
        if (all) {
            return [...document.querySelectorAll(el)]
        } else {
            return document.querySelector(el)
        }
    }

    /**
     * Page community table
     */
    if (select('#shared-decks-datatable')) {
        const sharedDecks_dt = new simpleDatatables.DataTable('#shared-decks-datatable', {
            layout: {
                top: "{search}",
                bottom: "{info}{pager}"
            },
            perPage: 50,
            labels: {
                placeholder: "Search decks...",
                noRow: "No decks to display",
                info: "Showing {start} to {end} of {rows} decks",
            },
        })
    }

	/**
     * TEST START: Go to the next Q on double click
     */
	 // GET CARD's tabs
	var card_tab_list = document.querySelectorAll('#myTab button')
	card_tab_list.forEach(tab_item => {
		var card_tab = new bootstrap.Tab(tab_item)
	})

	// GET answers' labels
	var card_answer_list = document.querySelectorAll("#myTabContent .card-answer-container label")
	const total_card = (card_answer_list.length)/3

	card_answer_list.forEach(answer_item => {
		answer_item.addEventListener("dblclick",  () => {
			var tab_id = answer_item.id.substring(14)
			var tab_target = `tab_card_target-${String(parseInt(tab_id)+1)}`

			if(parseInt(tab_id) == total_card){
				var card_tab_submit = document.querySelector('#myTab button[data-bs-target="#tab_card_target-submit"]')
				bootstrap.Tab.getInstance(card_tab_submit).show()
			}else{
				var card_tab_question = document.querySelector(`#myTab button[data-bs-target="#${tab_target}"]`)
				bootstrap.Tab.getInstance(card_tab_question).show()
			}
		})
	})
})()
