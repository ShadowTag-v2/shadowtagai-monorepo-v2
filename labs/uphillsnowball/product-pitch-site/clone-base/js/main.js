$(document).ready(function() {

    /*--------------------------------------------------------------
    ## Coloca o tamanho do body para sempre pegar a altura da janela e jogar o footer no fim
    --------------------------------------------------------------*/
    if (!$("body").hasClass("home"))
    $("body").addClass("interna");


    if ($('body').hasClass('interna')) {
        var height = (window).innerHeight;
        var fHeight = document.querySelector('.footer').offsetHeight;
    
        $('body').css('min-height', height);
        $('body').css('padding-bottom', fHeight);
    
        jQuery(window).resize(function(){
            var height = (window).innerHeight;
            var fHeight = $('footer').innerHeight;
    
            $('body.interna').css('min-height', height);
            $('body.interna').css('padding-bottom', fHeight);
        });   
    }

    /*--------------------------------------------------------------
    ## Abre/Fecha Menu mobile
    --------------------------------------------------------------*/
    if (window.matchMedia("screen and (max-width: 1199px)").matches) {
        '<div class="closeMenu js-trigger-menuClose"><img src="http://ri-auraminerals.mz-sites.com/wp-content/uploads/sites/418/2020/10/closeMenu.png"></div>'
    }
    $(".js-trigger-menu").click(function() {
        $(".js-target-menu").toggleClass("active");
    });
    $(".js-shutdown-menu").click(function () {
        $(".js-target-menu").toggleClass('active');
    });

    /*--------------------------------------------------------------
    ## Accordion
    --------------------------------------------------------------*/
    if ($(".accordion__item__header").length > 0) {
        $(".accordion__item__header").click(function() {
            $(this).toggleClass("active");
            $(this).next("div").slideToggle(200);
        });
    }

    /*--------------------------------------------------------------
    ## Add class fixed in header after certain window height
    --------------------------------------------------------------*/
    $(window).on("scroll",function(){
        $('.header').toggleClass('header--fixed',$(document).scrollTop()>25);
    });
    if ($(document).scrollTop()>10) {
        $('.header').addClass('header--fixed');
    }

    /*--------------------------------------------------------------
    ## Add state class internal on header if is not home
    --------------------------------------------------------------*/
    
    if (!$('body').hasClass('home'))
        $('.header').addClass('header--internal');

    /*--------------------------------------------------------------
    ## Remove hash# do href (href="#")
    --------------------------------------------------------------*/
    $("nav a[href='#']").removeAttr("href");
    

    /*--------------------------------------------------------------
    ## Acessibility Font Size
    --------------------------------------------------------------*/

    setTimeout(function() {
        var fontIndex = 3;
        var textElements = document.querySelectorAll('body, h1, h2, h3, h4, p, a, span, legend, li, label, input, select, button, div, td, th, text');
        var increaseFontElement = document.querySelector('.a11y__increase_font');
        var decreaseFontElement = document.querySelector('.a11y__decrease_font');
    
        increaseFontElement.addEventListener('click', function() {
            decreaseFontElement.style.opacity = 1;
    
            if ( fontIndex < 7 ) {
                fontIndex++;
                textElements.forEach(function(textElement) {
                    var size = parseInt(window.getComputedStyle(textElement).getPropertyValue('font-size')) + 2;
                    textElement.style.fontSize = size + 'px';
    
                    console.log(textElement);
                });
            }
    
            if ( fontIndex == 7 ) {
                increaseFontElement.style.opacity = 0.5;
            }
        });
    
        decreaseFontElement.addEventListener('click', function() {
            increaseFontElement.style.opacity = 1;
    
            if ( fontIndex > 0 ) {
                fontIndex--;
                textElements.forEach(function(textElement) {
                    var size = parseInt(window.getComputedStyle(textElement).getPropertyValue('font-size')) - 2;
                    textElement.style.fontSize = size + 'px';
    
                    console.log(textElement);
                });
            }
    
            if ( fontIndex == 0 ) {
                decreaseFontElement.style.opacity = 0.5;
            }
        });
    }, 3000);
    
    /*--------------------------------------------------------------
    ## Acessibility Contraste
    --------------------------------------------------------------*/
    
    var constrasElement = document.querySelector('.a11y__contrast');

    var Contrast = {
        storage: "contrastState",
        cssClass: "contrast",
        currentState: null,
        check: checkContrast,
        getState: getContrastState,
        setState: setContrastState,
        toogle: toggleContrast,
        updateView: updateViewContrast
    };

    var changeContrast = function() {
        Contrast.toogle();
    }

    function checkContrast() {
        this.updateView();
    }

    function getContrastState() {
        return localStorage.getItem(this.storage) === "true";
    }

    function setContrastState(state) {
        localStorage.setItem(this.storage, "" + state);
        this.currentState = state;
        this.updateView();
    }

    function updateViewContrast() {
        var body = document.body;

        if (this.currentState === null) this.currentState = this.getState();

        if (this.currentState) body.classList.add(this.cssClass);
        else body.classList.remove(this.cssClass);
    }

    function toggleContrast() {
        this.setState(!this.currentState);
    }

    constrasElement.addEventListener('click', changeContrast);

    Contrast.check();

    /*--------------------------------------------------------------
    ## Acessibility Contraste
    --------------------------------------------------------------*/

    document.addEventListener('keydown', function(event) {
        var altAndShift = event.altKey && event.shiftKey;

        if ( altAndShift && (event.code == 'Digit1' || event.which == 49) ) {
            $('html, body').animate( { scrollTop: $("body").offset().top }, 1000 );
        }

        if ( altAndShift && (event.code == 'Digit2' || event.which == 50) ) {
            $('html, body').animate( { scrollTop: 0 }, 1000 );
        }

        if ( altAndShift && (event.code == 'Digit3' || event.which == 51) ) {
            // ( $('body').attr('id') == 'lang-pt-br' ) ? document.location.href="/" : document.location.href="/en";

            document.location.href="/";
        }

        if ( altAndShift && (event.code == 'Digit4' || event.which == 52) ) {
            $('html, body').animate( { scrollTop: $(".footer").offset().top }, 1000 );
        }
    });

    // Popup
    const popup = document.querySelector(`[ref=popup]`);

    if (popup) {

        const closeButton = popup.querySelector(`[ref=close-popup]`);

        const closePopup = () => {
            popup.setAttribute(`aria-hidden`,`true`);
        } 

        // Close when clicking on X
        if (closeButton) {
            closeButton.addEventListener(`click`, () => {
                closePopup();
            })
        }

        // Close when pressing ESC
        document.addEventListener(`keydown`, (event) => {
            if (event.key === `Escape`) {
                closePopup();
            }
        })

        // Close when clicking outside the popup box
        popup.addEventListener(`click`, (event) => {
            if (event.target.closest(`[ref=popup-box]`) === null) {
                closePopup();
            }
        })

    }

});