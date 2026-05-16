////////// Companies / API

// Base URL
var BASE_API_URL = fmBase;
// Base API URL for CMS API
var BASE_API_CMS_URL = BASE_API_URL + "/api";

//TODO: Vai virar um array com IDs e Nome de compania
var COMPANIES = [
    {
        id: fmId,
        name: fmName,
    },
];

/// Returns selected company
var getSelectedCompany = function () {
    return COMPANIES[0].id;
};

//////////////////#########################################//////////////////

////////// Page Events

/// Shows Loading - Might be site global
var startLoading = function () {
    $("#data").hide();
    $("#loading").show();
};

/// Hides Loading - Might be site global
var stopLoading = function () {
    $("#data").show();
    $("#loading").hide();
};

//////////////////#########################################//////////////////

////////// Utils

// Get Files grouped by Category
var CMS_GET_FILES =
    BASE_API_CMS_URL +
    "/c/" +
    getSelectedCompany() +
    "/c/{0}/year/{1}/lang/{2}";
var getFilesGroupedByCategoryUrl = function (
    companyId,
    categoryId,
    year,
    lang,
    groupByQuarter,
    groupByYear
) {
    var targetUrl =
        BASE_API_CMS_URL +
        "/c/" +
        companyId +
        "/c/" +
        categoryId +
        "/year/" +
        year +
        "/lang/" +
        lang;

    if (groupByQuarter === true) targetUrl += "?byQuarter=true";
    if (groupByYear === true) targetUrl += "?byYear=true";

    return targetUrl;
};

/// Clear the tables
var clearTables = function () {
    var index = 1;
    var tableId = "#tabela_";
    while ($(tableId + index).length >= 1) {
        // $(tableId + index + " thead, tbody").remove();
        $(tableId + index + " tr," + tableId + index +  " td").remove();
        $("#table" + index).hide();
        index++;
    }
};

//fill not Year
var fillTableWithoutYear = function(categories, documents, language, year, baseUrl, mount) {
    var i = 0;
    categories.forEach(function (category) {
      if (category.orderByPublished != undefined) {
        if (category.orderByPublished) {
          documents = orderPublishedDate(documents)
        }
      }
      i++;
      console.log("Função correta.");
  
      documents.forEach(function (document) {
        if (document.internal_name == undefined || (document.internal_name === category.internal_name)) {
            console.log(document.file_title[0].toUpperCase() + document.file_title.slice(1));
          $('<tr>').append(
            '<td class="data">'+ formatShortDate(document, language) +'</td>'+
            '<td class="icone"><a href="' + (document.link_url || document.permalink) + '" target="_blank"><img src="' + category.icon + '" alt="' + document.file_title[0].toUpperCase() + document.file_title.slice(1) + '"/></a></td>'+
            '<td class="link"><a href="' + (document.link_url || document.permalink) + '" target="_blank">' + document.file_title[0].toUpperCase() + document.file_title.slice(1) + '</a></td>'
          ).appendTo('#tabela_' + i);
          $('#table' + i).show();
        }
      });
    });
  };
  
/// Clear the tables <ul> <li>
var clearTablesList = function () {
    var index = 1;
    var tableId = "#tabela_";
    while ($(tableId + index).length >= 1) {
        $(tableId + index + " .arquivos__list--item").remove();
        $("#table" + index).hide();
        index++;
    }
};

var clearTablesListFaq = function () {
    var index = 1;
    var tableId = "#fmFile_";
    while ($(tableId + index).length >= 1) {
        $(tableId + index + " .arquivos__list--item").remove();
        $("#table" + index).hide();
        index++;
    }
};

var formatShortDate = function (item, language) {
    var formatedDate = moment(item.file_published_date, "YYYYMMDD");
    if (language === "pt_BR") {
        return formatedDate.format("DD/MM/YYYY");
    } else {
        return formatedDate.format("MM/DD/YYYY");
    }
};

var formatShortDateHighlights = function (item, language) {
    var formatedDate = moment(item.file_published_date, "YYYYMMDD");
    if (language === "pt_BR") {
        return formatedDate.format("DD.MM.YYYY");
    } else {
        return formatedDate.format("MM.DD.YYYY");
    }
};

var formatAbbrDate = function (item, language) {
    var formatedDate = new String(item.file_published_date);
    if (language === "pt_BR") {
        var month = [
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez",
        ];
    } else {
        var month = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ];
    }
    return (
        "<time data-time=" +
        formatedDate +
        "><span>" +
        formatedDate.substring(8, 10) +
        "</span>" +
        month[formatedDate.substring(5, 7) - 1] +
        "</time>"
    );
};

var formatAbbrDateHome = function (item, language) {
    var formatedDate = new String(item.file_published_date);
    var month = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ];
    if (language === "pt_BR") {
        return (
            formatedDate.substring(8, 10) +
            "/" +
            month[formatedDate.substring(5, 7) - 1] +
            "/" +
            formatedDate.substring(0, 4)
        );
    } else {
        return (
            month[formatedDate.substring(5, 7) - 1] +
            "/" +
            formatedDate.substring(8, 10) +
            "/" +
            formatedDate.substring(0, 4)
        );
    }
};

var orderPublishedDate = function (array) {
    return array.sort(function (a, b) {
        return (
            new Date(b.file_published_date) - new Date(a.file_published_date)
        );
    });
};

var loadCategories = function (infoCategories) {
    internalNames = [];
    infoCategories.forEach(function (info) {
        internalNames.push(info.internal_name);
    });

    return internalNames;
};

/// Return the Url to Retrieve years given a set of subcategories
var getCategoryYearsURL = function (companyId) {
    return (
        BASE_API_URL +
        "/company/" +
        companyId +
        "/categoryInternalName/document/language/years"
    );
};

var getFilesByCategoriesUrl = function (companyId) {
    var targetUrl =
        BASE_API_URL + "/company/" + companyId + "/filter/categories/year/meta";

    return targetUrl;
};

var getFilesByCategoriesAllYearsUrl = function (companyId) {
    var targetUrl =
        BASE_API_URL + "/company/" + companyId + "/filter/categories/meta";

    return targetUrl;
};

//////////////////#########################################//////////////////

////////// Load Html Files

// Fill the table with datas
var fillHome = function (
    categories,
    documents,
    language,
    year,
    baseUrl,
    mount
) {
    if (categories[0].orderByPublished != undefined) {
        if (categories[0].orderByPublished) {
            documents = orderPublishedDate(documents);
        }
    }

    documents.slice(0, mount).forEach(function (document) {
        var str = document.file_title;
        if (str.length >= 63) {
            var fileName = str.substring(0, 63) + " ...";
        } else {
            var fileName = str.substring(0, 63);
        }
        $("<tr>")
            .append(
                $('<td class="data">').html(formatAbbrDate(document, language)),
                $('<td class="link">').append(
                    "<h3><a href='" +
                        (document.link_url || document.permalink) +
                        "' target='_blank'>" +
                        document.file_title +
                        "</a></h3>"
                ),
                $("</tr>")
            )
            .appendTo("#tabela_1");
        $("#table1").show();
    });
};

var fillHomeTable = function (
    categories,
    documents,
    language,
    year,
    baseUrl,
    mount
) {
    if (categories[0].orderByPublished != undefined) {
        if (categories[0].orderByPublished) {
            documents = orderPublishedDate(documents);
        }
    }
    documents.slice(0, mount).forEach(function (document) {
        $("<li>")
            .append(
                $(
                    "<a href='" +
                        (document.link_url || document.permalink) +
                        "' target='_blank'>"
                ).append(document.file_title + "</a>"),
                $("<span>").html(formatAbbrDateHome(document, language)),
                $("</li>")
            )
            .appendTo("#news");
    });
};

// Fill the table with datas
var fillHomeListHighlights = function (categories, documents, language, year, baseUrl, mount) {
    // console.log(categories[0].orderByPublished);
    if (categories[0].orderByPublished != undefined) {
        if (categories[0].orderByPublished) {
            documents = orderPublishedDate(documents);
        }
    }
  
    // console.log('documents', documents)
    documents.slice(0, mount).forEach(function(document) {
        $('<div class="b2iLibraryItem">').append(
            $('<span class="b2iLibraryItemDate">').text(formatShortDateHighlights(document, language)),
            $('<span class="b2iLibraryItemHeadline"><a class="b2iLibraryHeadlineLink b2iLibraryItemLink" href="'+(document.link_url || document.permalink)+'" target="_blank" title="' + document.file_title +'">' + document.file_title + '</a>'),
        $("</div>")                
        ).appendTo('.highlights-iq');
    });
};

// Fill the table with datas
var fillInternal = function (
    categories,
    documents,
    language,
    year,
    baseUrl,
    mount
) {
    var i = 0;
    _(categories).forEach(function (category) {
        if (category.orderByPublished != undefined) {
            if (category.orderByPublished) {
                documents = orderPublishedDate(documents);
            }
        }
        i++;

        documents.forEach(function (document) {
            if (document.internal_name === category.internal_name) {
                $("<tr>")
                    .append(
                        $('<td class="data">').text(
                            formatShortDate(document, language)
                        ),
                        $('<td class="icone">').append(
                            "<a href='" +
                                (document.link_url || document.permalink) +
                                "' target='_blank'><img src=\"" +
                                category.icon +
                                '" alt="' +
                                document.file_title +
                                '"/></a>'
                        ),
                        $('<td class="link">').append(
                            "<a href='" +
                                (document.link_url || document.permalink) +
                                "' target='_blank'>" +
                                document.file_title +
                                "</a>"
                        )
                    )
                    .appendTo("#tabela_" + i);
                $("#table" + i).show();
            }
        });
    });
};

// Fill the table with datas
var fillDownloadCenter = function (
    categories,
    documents,
    language,
    year,
    baseUrl,
    mount
) {
    var icon = categories[0].icon;
    var year = i18nShortQuarter + year.substring(2, 4);

    documents.forEach(function (document) {
        $("<li class='list-group-item'>")
            .append(
                $("<span>").text(formatShortDate(document, language)),
                $(
                    "<a href='" +
                        (document.link_url || document.permalink) +
                        "' target='_blank'>" +
                        document.file_title +
                        "</a>"
                ),
                $("</li>")
            )
            .appendTo("#tabela_" + document.file_quarter);
        $("#table" + document.file_quarter).show();
        $("#header_" + document.file_quarter).removeClass("inativo");
        $("#header_" + document.file_quarter).text(
            document.file_quarter + year
        );
    });
};

var fillResultsCenter = function (
    categories,
    documents,
    language,
    year,
    baseUrl
) {
    tableId = "#tabela_1";
    var yearDigitsWithQuarter = i18nShortQuarter + year.substring(2, 4);
    var headerQuarter = [
        '<th class="tabelatt ano">' + year + "</th>",
        '<th class="tabelatt icone">1' + yearDigitsWithQuarter + "</th>",
        '<th class="tabelatt icone">2' + yearDigitsWithQuarter + "</th>",
        '<th class="tabelatt icone">3' + yearDigitsWithQuarter + "</th>",
        '<th class="tabelatt icone">4' + yearDigitsWithQuarter + "</th>",
    ];

    $("<thead>")
        .prepend("<tr> " + headerQuarter.join(""))
        .appendTo(tableId);
    _(categories).forEach(function (category) {
        var allQuarters = [];
        allQuarters.push(
            '<td class="first titulo">' + category.title + "</td>"
        );
        for (var quarter = 1; quarter <= 4; quarter++) {
            var hasFind = false;
            documents.forEach(function (document) {
                if (
                    document.internal_name === category.internal_name &&
                    parseInt(document.file_quarter) === quarter
                ) {
                    hasFind = true;
                    allQuarters.push(
                        '<td class="icone"><a href=\'' +
                            (document.link_url || document.permalink) +
                            "' target='_blank'><img src=\"" +
                            category.icon +
                            '" alt="' +
                            document.file_title +
                            '"/></a></td>'
                    );
                }
            });
            if (!hasFind)
                allQuarters.push(
                    '<td class="icone off"><img src="' +
                        category.icon +
                        '" alt="' +
                        document.file_title +
                        '"/></td>'
                );
        }
        $("<tr> " + allQuarters.join("")).appendTo(tableId);
    });
    $("#table1").show();
};

///////////////////////////////////////////////////////////////
/// Retrieve documents from the CMS
///////////////////////////////////////////////////////////////
var mzcms = function (config) {
    var _this = this;
    this.config = config;

    //Fill the companies dropdown and fill table on the change
    this.fillCompanies = function () {
        $(this.config.companiesFieldId).change(function () {
            var selectedCompany = $(this).val();

            if (_this.config.enableDebug) {
                console.log(
                    "Selected Company " +
                        $(
                            _this.config.companiesFieldId + " option:selected"
                        ).text() +
                        " - " +
                        selectedCompany
                );
                console.log("Selected Category Id: " + _this.config.category);
            }
            _this.config.clearCallback(false);
            _this.fillYears(selectedCompany);
        });

        for (var i = 0; i < COMPANIES.length; i++) {
            $(_this.config.companiesFieldId).append(
                $("<option>", {
                    value: COMPANIES[i].id,
                    text: COMPANIES[i].name,
                })
            );
            if (i === 0)
                $(_this.config.companiesFieldId)
                    .val(COMPANIES[i].id)
                    .trigger("change");
        }
    };

    /// Fills the Years dropdown and maps the change in selected year
    this.fillYears = function (companyId) {
        var getYearsUrl = getCategoryYearsURL(companyId);
        $.ajax({
            type: "POST",
            url: getYearsUrl,
            data: JSON.stringify({
                categoryInternalNames: loadCategories(_this.config.categories),
                language_code: _this.config.language,
            }), // data
            success: function (response) {
                if (response.success) {
                    _this.formatYearsField(response.data);
                } else {
                    //TO-DO: Implement Error Handler
                }
            }, //success
            error: function (err) {
                //TO-DO: Implement Error Handler
            }, //error
            contentType: "application/json",
            dataType: "json",
        }); //ajax
    };

    //Get files on API by config options
    this.getFiles = function () {
        var url = "";
        var data = null;

        if (_this.config.groupByYear) {
            alert("NAO IMPLEMENTADO PARA LINX!!");
        } else if (_this.config.groupByQuarter) {
            url = getFilesGroupedByCategoryUrl(
                getSelectedCompany(),
                loadCategories(_this.config.categories),
                this.getSelectedYear(),
                _this.config.language,
                true,
                false
            );
        } else if (_this.config.getAllYears) {
            url = getFilesByCategoriesAllYearsUrl(getSelectedCompany());
            var data = {
                categoryInternalNames: loadCategories(_this.config.categories),
                language: _this.config.language,
                published: true,
            };
        } else {
            url = getFilesByCategoriesUrl(getSelectedCompany());
        }

        _this.config.loadingCallback();
        var year = _this.getSelectedYear();

        if (data == null) {
            var data = {
                year: year,
                categories: loadCategories(_this.config.categories),
                language: _this.config.language,
                published: true,
            };
        }

        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(data), //data
            success: function (res) {
                if (res.success) {
                    _this.config.fillCallback(
                        _this.config.categories,
                        res.data.document_metas,
                        _this.config.language,
                        year,
                        _this.config.baseUrl,
                        _this.config.mount
                    );
                    _this.config.loadedCallback();
                } else {
                    _this.config.loadedCallback();
                    //TO-DO: Handle Error
                }
            }, //success
            contentType: "application/json",

            dataType: "json",
        }); //ajax
    };

    /// Formats the Years Field and trigger the change to the first year to load the documentation
    this.formatYearsField = function (years) {
        if (years.length <= 0) {
            $(_this.config.yearsFieldId).hide();
            //_this.config.emptyFilesCallback();
        } else {
            $(_this.config.yearsFieldId).show();
        }

        for (var i = 0; i < years.length; i++) {
            $(_this.config.yearsFieldId).append(
                $("<option>", {
                    value: years[i],
                    text: years[i],
                })
            );
            if (i === 0)
                $(_this.config.yearsFieldId).val(years[i]).trigger("change");
        }
    };

    /// Returns selected year
    this.getSelectedYear = function () {
        if (_this.config.getAllYears) {
            return -1;
        } else {
            return $(_this.config.yearsFieldId).val();
        }
    };

    //Event change on dropdown year
    $(this.config.yearsFieldId).change(function () {
        var selectedYear = $(this).val();
        if (!selectedYear) {
            return;
        }
        _this.config.clearCallback(true);
        _this.getFiles();
    });

    /// Initializes the component
    this.init = function () {
        if (_this.config.getAllYears) {
            _this.getFiles();
        } else if (!_this.config.getByCompanies) {
            _this.fillYears(getSelectedCompany());
        } else {
            _this.fillCompanies();
        }
    };
};
