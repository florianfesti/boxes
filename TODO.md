[x] score config category

* rename:
    * label_radius to score_radius
    * label_invert to score_inv
* Put all in score config in a dedicated category
    * score_min + score_max + score_radius + score_inv

[x] Page generator number of column selector

* add a selector to choose the number of column in the main page
* only allow 4,5,6 columns choice

[x] For the notch generator in [game_counter_ring.py](boxes/generators/game/game_counter_ring.py)

* make the notch symmetrical shape (currently it is not), actual shape can be an option for the user to choose between a
  symmetrical or asymmetrical shape
