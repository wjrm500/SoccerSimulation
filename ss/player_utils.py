import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import dates as mdates


def show_predicted_ratings(player):
    age_list, predicted_rating_list = [], []
    for age in range(15, 40):
        age_list.append(age)
        predicted_rating = player.calculate_rating(age)
        predicted_rating_list.append(predicted_rating)
    age_array = np.array(age_list)
    predicted_rating_array = np.array(predicted_rating_list)
    x, y = age_array, predicted_rating_array
    plt.plot(x, y)
    for xy in zip(x, y):
        plt.text(
            xy[0] - 0.5,
            xy[1],
            int(xy[1]),
            {
                "weight": "bold",
                "size": 10,
            },
        )
    plt.title(
        f"Predicted Ratings for {player.name} over time",
        fontdict={"weight": "bold"},
    )
    plt.xlabel("Age")
    plt.ylabel("Predicted Rating")
    plt.axvline(x[np.argmax(y)], color="lightgray", linestyle="--")
    plt.show()


def plot_player(player, axes, config, date=None):
    labels_on, _, projection_on, scale_for_overall_rating_on = list(config.values())
    blank = True if player is None else False
    axes.set(aspect="equal")
    frame_size = 2.5
    frame_size = frame_size * 100 if scale_for_overall_rating_on else frame_size

    if not blank:
        ### Calculate vertices
        skill_distribution = player.get_skill_distribution(player.get_age_on_date(date))
        player_rating = player.ratings[date]["rating"] if date is not None else player.rating
        points = {}
        for j, (skill, value) in enumerate(skill_distribution.items()):
            if scale_for_overall_rating_on:
                value *= player_rating
            angle = 2 / len(skill_distribution) * j * np.pi
            point_x = value * np.sin(angle)
            point_y = value * np.cos(angle)
            points[skill] = {"x": point_x, "y": point_y}
            if labels_on:
                side_point_x = frame_size * np.sin(angle)
                side_point_y = frame_size * np.cos(angle)
                label_x = 290 * np.sin(angle)
                label_y = 290 * np.cos(angle)
                axes.plot((0, side_point_x), (0, side_point_y), color="blue", linewidth=0.25)
                label_text = (
                    f"{skill.capitalize()}\n{int(value)}"
                    if scale_for_overall_rating_on
                    else f"{skill}\n{value:.1%}"
                )
                axes.text(
                    label_x,
                    label_y,
                    label_text,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontdict={"family": "arial", "size": 15},
                )
        points_list = list(points.values())
        points_list.append(
            points_list[0]
        )  ### Duplicate first point as last point to complete the shape

        ### Add edges between vertices
        for j in range(len(points_list) - 1):
            axes.plot(
                (points_list[j]["x"], points_list[j + 1]["x"]),
                (points_list[j]["y"], points_list[j + 1]["y"]),
                color="black",
            )

        ### Add rating projection to plot
        if projection_on and player.age != player.peak_age:
            projected_skill_distribution = player.get_skill_distribution(player.peak_age)
            projected_player_rating = player.get_rating(age=player.peak_age)
            projected_points = {}
            for j, (skill, projected_value) in enumerate(projected_skill_distribution.items()):
                if scale_for_overall_rating_on:
                    projected_value *= projected_player_rating
                angle = 2 / len(projected_skill_distribution) * j * np.pi
                projected_point_x = projected_value * np.sin(angle)
                projected_point_y = projected_value * np.cos(angle)
                projected_points[skill] = {"x": projected_point_x, "y": projected_point_y}
            projected_points_list = list(projected_points.values())
            projected_points_list.append(
                projected_points_list[0]
            )  ### Duplicate first point as last point to complete the shape

            ### Add edges between vertices
            projected_line_colour = "green" if player.age < player.peak_age else "red"

            for j in range(len(projected_points_list) - 1):
                axes.plot(
                    (projected_points_list[j]["x"], projected_points_list[j + 1]["x"]),
                    (projected_points_list[j]["y"], projected_points_list[j + 1]["y"]),
                    color=projected_line_colour,
                    linestyle="dotted",
                )

    if not blank:
        x_points = [point["x"] for point in points_list]
        y_points = [point["y"] for point in points_list]
    else:
        x_points = [frame_size, frame_size, -frame_size, -frame_size]
        y_points = [frame_size, -frame_size, -frame_size, frame_size]
    axes.fill(x_points, y_points, color="lightgray")

    ### Miscellaneous config
    axes.set_xlim(-frame_size, frame_size)
    axes.set_ylim(-frame_size, frame_size)
    axes.axis("off")
    if not blank and not labels_on:
        axes.plot(0, 0, "o")


def show_skill_distribution(
    players, date=None, labels=None, projection=False, scale_for_overall_rating=True
):
    if not isinstance(players, list):
        players = [players]
    num_players = len(players)
    if num_players > 10:
        print("Too many players")
        return
    if labels is None:
        if num_players > 2:
            labels = False
        else:
            labels = True
    position_text_rotated = True if num_players > 2 else False
    plot_config = {
        "labelsOn": labels,
        "positionTextRotated": position_text_rotated,
        "projectionOn": projection,
        "scaleForOverallRatingOn": scale_for_overall_rating,
    }
    rows = 1 if num_players < 3 else 2
    cols = math.ceil(num_players / rows)
    fig, axes = plt.subplots(nrows=rows, ncols=cols)
    if num_players == 1:
        plot_player(players[0], axes, plot_config, date)
    elif num_players == 2:
        for i in range(cols):
            plot_player(players[i], axes[i], plot_config, date)
    else:
        p = 0
        for i in range(rows):
            for j in range(cols):
                if p < num_players:
                    plot_player(players[p], axes[i][j], plot_config, date)
                else:
                    plot_player(None, axes[i][j], plot_config, date)
                p += 1

    # ### Show plot
    # plt.show()
    plt.tight_layout()
    return fig


def show_player_form(player):
    fig = plt.figure()
    fig.add_subplot(111)
    x = list(player.forms.keys())
    y = list(player.forms.values())
    x = mdates.date2num(x)
    plt.axis("off")
    plt.plot_date(x, y, "b-")
    return fig


def show_player_development(player, date=None):
    fig = plt.figure()
    fig.add_subplot(111)
    if date is not None:
        x = range(len([k for k in player.ratings.keys() if k <= date]))
        y_r = [v["rating"] for k, v in player.ratings.items() if k <= date]
        y_pr = [v["peak_rating"] for k, v in player.ratings.items() if k <= date]
    else:
        x = range(len(player.ratings.keys()))
        y_r = [v["rating"] for v in player.ratings.values()]
        y_pr = [v["peak_rating"] for v in player.ratings.values()]
    plt.title("Development Graph", fontsize=14)
    plt.xlabel("Day", fontsize=12, labelpad=8)
    plt.ylabel("Rating", fontsize=12, labelpad=8)
    fade_range = 10
    for plot, color_tuple in zip([y_r, y_pr], [[0, 0, 1], [0.68, 0.85, 0.90]]):
        for i in range(0, fade_range + 1):
            for y, strength in zip(
                [plot[0], plot[-1]], [1 - (i / fade_range), 0 + (i / fade_range)]
            ):
                plt.gca().axhline(
                    y,
                    (1 / fade_range) * i - (1 / fade_range),  ### xmin
                    (1 / fade_range) * i,  ### xmax
                    color=color_tuple + [strength],
                    linestyle="--",
                    linewidth=max(strength, 0.1),
                )
    plt.plot(x, y_r, "b-")
    plt.plot(x, y_pr, color="lightblue", linestyle="solid")
    return fig
