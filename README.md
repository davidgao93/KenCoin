<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/davidgao93/KenCoin">
    <img src="images/bitcoin.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">KenCoin</h3>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

KenCoin.py is a simple Discord bot with the sole purpose of tracking the number of KenCoins a user has.

### Built With

* [Python](https://www.python.org/)
* [Discord.py](https://discordpy.readthedocs.io/en/stable/)

<!-- GETTING STARTED -->
## Getting Started

To setup your own KenCoin bot:

### Prerequisites

Python3
* pip
  ```sh
# Windows
py -3.8 -m pip install discord.py apscheduler git+https://github.com/Rapptz/discord-ext-menus
  ```

### Installation

1. Get a new bot + free token at [Discord Developers](https://discord.com/developers/applications)
2. Clone the repo
   ```sh
   git clone https://github.com/davidgao93/KenCoin.git
   ```
3. Create token.0 file in /lib/bot and paste in your token
4. Edit your GuildID in `/lib/bot/__init__.py`
   ```Python
   self.guild = self.get_guild('ENTER_YOUR_GUILDID')
   ```
5. Run bot using launcher.py


<!-- ROADMAP -->
## Roadmap

* Banking feature
* Exp/Level system
* Gear slots

<!-- CONTRIBUTING -->
## Contributing

Not really sure why you would contribute to this but any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

No License.


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Carberra](https://github.com/Carberra/updated-discord.py-tutorial)

