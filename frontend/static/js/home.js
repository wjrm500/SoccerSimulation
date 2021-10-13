let customClubs = [];

$(document).ready(function () {
    $('.simulation-button').click(function () {
        $(this).find('#text').hide();
        $(this).find('#spinner').show();
        window.location.href = $(this).data('url');
    });

    $('#existing-simulation-form').submit(function (e) {
        let simulateButton = $(this).find('.simulate-button')
        simulateButton.find('#text').hide();
        simulateButton.find('#spinner').show();
        return true;
    });

    $('#existing-how').change(function() {
        let val = $(this).val();
        $('.hideable-div').css('display', 'none');
        $('.hideable-div input').prop('required', false);
        let divToShow = $(`#${val}`);
        divToShow.css('display', 'flex');
        divToShow.find('input').prop('required', true);
    });

    setTimeout(function() {
        $('#error').slideUp();
    }, 2000);

    $('#add-custom-club-button').click(function(e) {
        e.preventDefault();
        $('#custom-club-error').html('');
        let customClub = $('#custom-club').val();
        $('#custom-club').val('').focus();
        customClub = customClub.charAt(0).toUpperCase() + customClub.slice(1);
        let regex = new RegExp('^[A-Za-z]+$');
        let passedRegex = regex.test(customClub);
        let notDuplicate = !customClubs.includes(customClub);
        let errors = [];
        if (!passedRegex) {
            errors.push('Custom club names can only include standard English alphabetic characters')
        }
        if (!notDuplicate) {
            errors.push('Custom club names must be unique');
        }
        if (errors.length != 0) {
            let errorString = errors.join('\n');
            $('#custom-club-error').html(errorString);
        } else {
            customClubs.push(customClub);
            $('#custom-clubs').show();
            let divElem = $('<div>')
                .addClass('custom-club-container');
            let clubName = $('<span>')
                .html(customClub)
                .addClass('custom-club-text')
            let removeButton = $('<span>')
                .html('✕')
                .addClass('custom-club-remove-button');
            clubName.appendTo(divElem);
            removeButton.appendTo(divElem);
            divElem.appendTo($('#custom-clubs-list'));
            addRemoveCustomClubEventHandler(removeButton);
        }
    });

    $('#new-simulation-form').submit(function() {
        $('#custom-club-error').html('');
        if ($('#num-clubs').val() < customClubs.length) {
            $('#custom-club-error').html('Too many custom clubs specified');
            return false;
        }
        let simulateButton = $(this).find('.simulate-button')
        simulateButton.find('#text').hide();
        simulateButton.find('#spinner').show();
        let hiddenInput = $('<input type="hidden">');
        hiddenInput.attr('name', 'custom-clubs');
        hiddenInput.attr('value', JSON.stringify(customClubs));
        hiddenInput.appendTo($(this));
        return true;
    });
});

function addRemoveCustomClubEventHandler(customClubRemoveButton) {
    customClubRemoveButton.click(function() {
        let divElem = $(this).closest('.custom-club-container');
        let clubName = divElem.find('.custom-club-text').html();
        let removeIndex = customClubs.indexOf(clubName);
        if (removeIndex != -1) {
            customClubs.splice(removeIndex, 1);
        }
        divElem.remove();
        if ($('#custom-clubs-list > div').length == 0) {
            $('#custom-clubs').hide();
        }
        console.log(customClubs);
    });
}