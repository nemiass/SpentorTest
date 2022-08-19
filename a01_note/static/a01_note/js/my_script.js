(function () {
  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim();
    if (all) {
      return [...document.querySelectorAll(el)];
    } else {
      return document.querySelector(el);
    }
  };

  /**
   * EmojioneArea
   */
  $(".emojiPicker").emojioneArea({
    // FIXME: The input and the plugin (responsible) don't match at all.
    pickerPosition: "right", // 'top' | 'right' | 'bottom'
    filtersPosition: "bottom", // 'top' | 'bottom'
    saveEmojisAs: "unicode",
    search: true,
    standalone: true,
    tones: true,
    hideSource: true,
    shortcuts: false,
  });

  /**
   * Toggle sidebar icon (hamburger)
   */
  const icon_hamburger = "bi-list";
  const icon_left = "bi-chevron-double-left";
  const icon_right = "bi-chevron-double-right";

  const sidebarBtn = document.querySelector("#toggle-sidebar-btn");
  const body_toggle = document.querySelector("body");

  sidebarBtn.addEventListener("mouseover", () => {
    if (body_toggle.classList.contains("toggle-sidebar")) {
      sidebarBtn.classList.remove(icon_hamburger, icon_left);
      sidebarBtn.classList.add(icon_right);
    } else {
      sidebarBtn.classList.remove(icon_hamburger, icon_right);
      sidebarBtn.classList.add(icon_left);
    }
  });

  sidebarBtn.addEventListener("mouseleave", () => {
    if (body_toggle.classList.contains("toggle-sidebar")) {
      sidebarBtn.classList.remove(icon_right);
    } else {
      sidebarBtn.classList.remove(icon_left);
    }
    sidebarBtn.classList.add(icon_hamburger);
  });

  sidebarBtn.addEventListener("click", () => {
    if (body_toggle.classList.contains("toggle-sidebar")) {
      sidebarBtn.classList.remove(icon_right);
    } else {
      sidebarBtn.classList.remove(icon_left);
    }
    sidebarBtn.classList.add(icon_hamburger);
  });

  /**
   * Page community table
   */
  if (select("#shared-pages-datatable")) {
    const sharedPages_dt = new simpleDatatables.DataTable(
      "#shared-pages-datatable",
      {
        layout: {
          top: "{search}",
          bottom: "{info}{pager}",
        },
        perPage: 50,
        labels: {
          placeholder: "Search pages...",
          noRow: "No pages to display",
          info: "Showing {start} to {end} of {rows} pages",
        },
      }
    );
  }

  /**
   * Clipboard: Page link
   */
  // Clipboard instance
  if (select("#copy-pagelink")) {
    var clipboardTrigger = select("#copy-pagelink");
    var clipboard = new ClipboardJS(clipboardTrigger);

    // Toast notification
    var toastTrigger = select("#copy-pagelink");
    var toastLiveClipboard = select("#clipboardToast");
    if (toastTrigger) {
      toastTrigger.addEventListener("click", function () {
        var toast = new bootstrap.Toast(toastLiveClipboard);
        toast.show();
      });
    }
  }

  /**
   * Show deck's tab pane using the URL's hash
   */
  function removeHashUrl() {
    var cleaned_url = window.location.href.split("#")[0];
    window.history.replaceState({}, document.title, cleaned_url);
  }
  var deckUrlHash = window.location.hash;
  if (deckUrlHash === "#deck-detail") {
    var triggerBtn = select(
      `#page-nav-tab button[data-bs-target="${deckUrlHash}"]`
    );
    var deckTab = new bootstrap.Tab(triggerBtn);
    deckTab.show();
  } else {
    removeHashUrl();
  }

  /**
   * Autocomplete inputs for Disease's summary form
   */
  // Cie10's input
  var cie10FormInput = $("#cie10");
  var cie10SearchInput = $("#ui-cie10");
  var cie10Endpoint = cie10SearchInput.attr("data-cie10-endpoint");

  cie10SearchInput.autocomplete({
    minLength: 3,
    source: cie10Endpoint,
    focus: (event, ui) => {
      event.preventDefault();
      cie10SearchInput.val(ui.item.label);
      cie10FormInput.val(ui.item.value);
    },
    select: (event, ui) => {
      event.preventDefault();
      cie10SearchInput.val(ui.item.label);
      cie10FormInput.val(ui.item.value);
    },
  });

  // Symptom's input
  var symptomFormInput = $("#symptom");
  var symptomSearchInput = $("#ui-symptom");
  var symptomEndpoint = symptomSearchInput.attr("data-symptom-endpoint");
  var symptomList = $("#symptom-list");
  var symptomIdArray = [];

  if (symptomFormInput.val() !== "") {
    symptomIdArray = symptomFormInput.val().split(",");
  }
  symptomSearchInput.autocomplete({
    minLength: 3,
    source: symptomEndpoint,
    focus: (event, ui) => {
      event.preventDefault();
      symptomSearchInput.val("");
    },
    select: (event, ui) => {
      event.preventDefault();
      symptomSearchInput.val("");

      // Add selected symptom to the array
      symptomIdArray.push(ui.item.value);
      symptomFormInput.val(symptomIdArray);

      // Show selected symptom inside the form
      var htmlContent = `
      <li class="list-group-item py-1 px-2">
          <button type="button" class="btn btn-warning btn-sm me-2 app-btn-sm"
              disabled
          >
              <i class="bi bi-trash2-fill"></i>
          </button>
          <span style="font-size: 14px;">
              ${ui.item.label}
          </span>
      </li>
      `;
      symptomList.append(htmlContent);
    },
  });

  // Drug's input
  var drugFormInput = $("#drug");
  var drugSearchInput = $("#ui-drug");
  var drugEndpoint = drugSearchInput.attr("data-drug-endpoint");
  var drugList = $("#drug-list");
  var drugIdArray = [];

  if (drugFormInput.val() !== "") {
    drugIdArray = drugFormInput.val().split(",");
  }
  drugSearchInput.autocomplete({
    minLength: 3,
    source: drugEndpoint,
    focus: (event, ui) => {
      event.preventDefault();
      drugSearchInput.val("");
    },
    select: (event, ui) => {
      event.preventDefault();
      drugSearchInput.val("");

      // Add selected drug to the array
      drugIdArray.push(ui.item.value);
      drugFormInput.val(drugIdArray);

      // Show selected drug inside the form
      var htmlContent = `
      <li class="list-group-item py-1 px-2">
          <button type="button" class="btn btn-warning btn-sm me-2 app-btn-sm"
              disabled
          >
              <i class="bi bi-trash2-fill"></i>
          </button>
          <span style="font-size: 14px;">
              ${ui.item.label}
          </span>
      </li>
      `;
      drugList.append(htmlContent);
    },
  });
})();
