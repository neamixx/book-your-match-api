# book-your-match

Endpoints

Users

1. POST (/users/register)
    - Register a User 

2. POST (/users/login)
    - Log in a User

3. GET (/users/)
    - Get all users in the system

4. GET (/users/me)
    - Get logged user

5. POST (/users/logout)
    - Log out user

6. POST (/users/{id}/embedding)
    - Update the user embedding

7. GET (/users/{id})
    - Get a user by id


Groups

1. GET (/groups/)
    - Get all groups in the system

2. POST (/groups/create)
    - Create a group

3. GET (/groups/relation)
    - Get the relation in a group

4. POST (groups/join)
    - Join to a group

5. GET (/groups/{group_name})
    - Get a group by name

6. GET (/groups/by-user/{email})
    - Get user groups by email


Cities

1. POST (/city/create)
    - Create a new city in the system

2. POST (/city/set-airport)
    - Set an airport to a city

3. GET (/city/all)
    - Get all cities in the system

4. GET (/city/{name})
    - Get a city by name
5. POST (/city/{city_name}/embedding)
    - Set or modify the embedding by city name


Cards

1. POST (/create)
    - Create a card

2. GET (/card)
    - Get a random card

3. POST (/card)
    - Alter the algorithm to the embedding of the user

4. GET (/cards)
    - Get all cards in the system

5. POST (/{id}/embedding)
    - Set or modify the embedding by card id


SkyScanner

1. POST (/skyscanner/cheapest-flights)
    - You get the cheapest flight from A to B
2. POST (/skyscanner/airports)
    - You get all flights from A to B


Default

1. POST (/recomanar)
    - Reccomends a City to a group