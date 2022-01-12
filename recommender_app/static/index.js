window.onload = function sketch() {

    genres = {'genre_action': 'Action', 'genre_adventure': 'Adventure', 'genre_animation': 'Animation',
    'genre_children': 'Children', 'genre_comedy': 'Comedy', 'genre_crime': 'Crime', 'genre_documentary': 'Documentary',
    'genre_drama': 'Drama', 'genre_fantasy': 'Fantasy', 'genre_film_noir': 'Noir', 'genre_horror': 'Horror',
    'genre_imax': 'IMAX', 'genre_musical': 'Musical', 'genre_mystery': 'Mystery', 'genre_romance': 'Romance',
    'genre_sci_fi': 'Sci-Fi', 'genre_thriller': 'Thriller', 'genre_war': 'War', 'genre_western': 'Western'}

    // Div for submitting ratings inputs
    var inputRatingsDiv = $("#input__ratings");

    // Button for adding a new input rating
    var addInputRatingBtn = $("#input__rating-button__add");
    addInputRatingBtn.on("click", createRatingsDiv);

    function createRatingsDiv(){
        // Get current Input Ratings
        var inputRatings = $('.input__rating');

        // Make the next index equal to the number of ratings plus one
        var rating_index = inputRatings.length + 1;

        // If there are already 20 ratings, don't add any more
        if (rating_index > 20){
            return null
        }

        // Create div for the rating
        var div = $("<div/>")
        div.innerHTML = "Rate movie: ";
        div.addClass("input__rating");
        div.prop("rating_index",rating_index);
        div.addClass('input__rating-index__' + rating_index);
        div.insertBefore(addInputRatingBtn);

        // Create a genre selection drop down for the rating
        var genre_dropdown = $("<select/>");
        genre_dropdown.addClass("input__rating-genre__select");
        genre_dropdown.prop("rating_index", rating_index);
        div.append(genre_dropdown);

        // Add an All genre option
        var option = $("<option/>", {value: "All", text: "All"});
        genre_dropdown.append(option);

        // Populate the genre selection dropdown
        for (const [key_i, value_i] of Object.entries(genres)) {
            var option = $("<option/>", {value: key_i, text: value_i});
            genre_dropdown.append(option);
        }

        // Create a movie selection drop down for the rating
        var movie_dropdown = $("<select/>");
        movie_dropdown.addClass("input__rating-movie__select");
        movie_dropdown.prop("rating_index", rating_index);
        div.append(movie_dropdown);

        // Add a not seen option
        var options = [{value: -1, text: "None", movies_count: 0}];

        // Populate the options with the movies
        for (var j = 0; j < data.length; j++){
            var option = {value: data[j].id,
            text: data[j].title,
            movies_count: data[j].movies_count}
            options.push(option)
        }
        movie_dropdown.selectize({
        options: options,
        valueField: 'value',
        labelField: 'text',
        maxItems: 1,
        });

        movie_dropdown[0].selectize.addItem(-1);
    }

    // Create 5 Ratings Divs
    for (var i = 0; i < 5; i++){
        createRatingsDiv();
    }

    // Add a listener to the genre dropdowns that re-populates the movies based on the selected genre
    var genre_dropdowns = $('.input__rating-genre__select');
    genre_dropdowns.on("change", filterMoviesDropdown)

    // When the genre is selected, find only the movies with that genre and re-populate
    function filterMoviesDropdown() {

        // Get the index of the rating
        rating_index = this.rating_index;
        genre_selected = this.value;

        // Select the corresponding movie dropdown
        var movie_dropdown = $('.input__rating-index__' + rating_index + ' .input__rating-movie__select');

        // Get the current selection
        movie_dropdown = movie_dropdown[0].selectize;
        var movie_selected = movie_dropdown.items[0];

        // Remove all of the current options
        movie_dropdown.clear();
        movie_dropdown.clearOptions();

        // Add a not seen option
        var options = [{value: -1, text: "None", movies_count: 0}]

        // Iterate through all of the movies filtering by the chosen genre
        for (var j = 0; j < data.length; j++){
            // If the genre is All always add all movies as an option
            if (genre_selected == "All"){
                var option = {value: data[j].id,
                text: data[j].title,
                movies_count: data[j].movies_count}
                options.push(option)
            }
            // Otherwise only push items that are matching the genre
            else if (data[j][genre_selected]){
                var option = {value: data[j].id,
                text: data[j].title,
                movies_count: data[j].movies_count}
                options.push(option)
            }
        }

        movie_dropdown.addOption(options);

        // Select None as the Item
        movie_dropdown.addItem(-1);
        // Try and select the previously selected movie as the Item
        movie_dropdown.addItem(movie_selected);
    }
}