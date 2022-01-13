window.onload = function sketch() {

    genres = {'genre_action': 'Action', 'genre_adventure': 'Adventure', 'genre_animation': 'Animation',
    'genre_children': 'Children', 'genre_comedy': 'Comedy', 'genre_crime': 'Crime', 'genre_documentary': 'Documentary',
    'genre_drama': 'Drama', 'genre_fantasy': 'Fantasy', 'genre_film_noir': 'Noir', 'genre_horror': 'Horror',
    'genre_imax': 'IMAX', 'genre_musical': 'Musical', 'genre_mystery': 'Mystery', 'genre_romance': 'Romance',
    'genre_sci_fi': 'Sci-Fi', 'genre_thriller': 'Thriller', 'genre_war': 'War', 'genre_western': 'Western'};

    ratings_options = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5];

    // Div for submitting ratings inputs
    var inputRatingsDiv = $("#input__ratings");

    // Button for adding a new input rating
    var addInputRatingBtn = $("#input__rating-button__add");
    addInputRatingBtn.on("click", createRatingsDiv);

    // Create a ratings div
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
        var div = $("<div><br>Rate Movie " + rating_index +": </div>")
        div.addClass("input__rating");
        div.prop("rating_index",rating_index);
        div.addClass('input__rating-index__' + rating_index);
        div.insertBefore(addInputRatingBtn);

        // Create a genre selection drop down for the rating
        var label = $('<label for="genres">Genre:<br></label>');
        var genre_dropdown = $('<select class="input__rating-genre__select" form="input-ratings-form" name="genres"/>');
        var sub_div = $("<div/>");
        genre_dropdown.addClass("input__rating-genre__select");
        genre_dropdown.prop("rating_index", rating_index);
        sub_div.append(label);
        sub_div.append(genre_dropdown);
        div.append(sub_div);

        // Add an All genre option
        var option = $("<option/>", {value: "All", text: "All"});
        genre_dropdown.append(option);

        // Populate the genre selection dropdown
        for (const [key_i, value_i] of Object.entries(genres)) {
            var option = $("<option/>", {value: key_i, text: value_i});
            genre_dropdown.append(option);
        }

        // Create a movie selection drop down for the rating
        var label = $('<label for="movies">Movie:</label>');
        var movie_dropdown = $('<select class="input__rating-movie__select" form="input-ratings-form" name="movies"/>');
        sub_div = $("<div/>");
        movie_dropdown.prop("rating_index", rating_index);
        sub_div.append(label);
        sub_div.append(movie_dropdown);
        div.append(sub_div);

        // Add a not seen option
        var options = [{value: -1, text: "None", movies_count: 0}];

        // Populate the options with the movies
        for (const movie of data){
            var option = {value: movie.id,
            text: movie.title,
            movies_count: movie.movies_count}
            options.push(option)
        }
        movie_dropdown.selectize({
        options: options,
        valueField: 'value',
        labelField: 'text',
        maxItems: 1,
        });

        movie_dropdown[0].selectize.addItem(-1);

        // Create a genre selection drop down for the rating
        var label = $('<label for="ratings">Rating:<br></label>');
        var rating_dropdown = $('<select class="input__rating-rating__select" form="input-ratings-form" name="ratings"/>');
        var sub_div = $("<div/>")
        rating_dropdown.prop("rating_index", rating_index);
        sub_div.append(label);
        sub_div.append(rating_dropdown);
        div.append(sub_div);

        var option = $("<option/>", {value: -1, text: "None"});
        rating_dropdown.append(option);

        // Populate the genre selection dropdown
        for (const rating of ratings_options) {
            var option = $("<option/>", {value: rating, text: rating});
            rating_dropdown.append(option);
        }
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
        for (const movie of data){
            // If the genre is All always add all movies as an option
            if (genre_selected == "All"){
                var option = {value: movie.id,
                text: movie.title,
                movies_count: movie.movies_count}
                options.push(option)
            }
            // Otherwise only push items that are matching the genre
            else if (movie[genre_selected]){
                var option = {value: movie.id,
                text: movie.title,
                movies_count: movie.movies_count}
                options.push(option)
            }
        }

        movie_dropdown.addOption(options);

        // Select None as the Item
        movie_dropdown.addItem(-1);
        // Try and select the previously selected movie as the Item
        movie_dropdown.addItem(movie_selected);
    }

    var form = $('#input-ratings-form');
    form.on('submit', async (e) => {
      e.preventDefault(); // Prevent default form submit behaviour

      var form_data = new FormData(form[0]);
      var movie_recommendations_div = $('#movie__recommendations');
      movie_recommendations_div.text("Loading your recommendations...");

      const response = await fetch('/handle_data', {
        method: 'POST',
        body: form_data
      });

      if (response.ok) {
        // success
        const response_json = await response.json();
        console.log(response_json);

        movie_recommendations_div.text("Your Movie Recommendations:");
        // Create div for the rating
        var div = $("<div/>");
        div.addClass("movie__recommendation");
        div.text("Ayo");
        movie_recommendations_div.append(div);

        var movie_recommendations = response_json['body'];

        var recommendations_table = $('<table id="movie__recommendations-table"></table>');
        movie_recommendations_div.append(recommendations_table);

        var table_row = $('<tr/>');
        recommendations_table.append(table_row);

        var table_col = $('<th>Name</th>');
        table_row.append(table_col);
        table_col = $('<th>Match</th>');
        table_row.append(table_col);
        table_col = $('<th>URL</th>');
        table_row.append(table_col);

        for (const movie_recommendation of movie_recommendations.slice(0,20)){
            table_row = $('<tr/>');
            recommendations_table.append(table_row);

            table_col = $('<td/>');
            table_col.text(movie_recommendation.title);
            table_row.append(table_col);

            table_col = $('<td/>');
            table_col.text(movie_recommendation.rating/5);
            table_row.append(table_col);

            table_col = $('<td/>');
            table_col.text("url");
            table_row.append(table_col);
        }



      } else {
        // error
      }
    }
    );
}