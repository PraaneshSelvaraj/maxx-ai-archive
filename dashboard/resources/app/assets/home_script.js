async function getCurrentSong() {
    const d = {
      name: 'Offline',
      artist: '',
      artwork: 'images/music.svg',
      state: 'paused',
      volume: 100,
      srcPosition: 0,
      srcMax: 100,
    };
    try {
      const uri = `http://127.0.0.1:8080/requests/status.xml`;
      const response = await fetch(uri, {
        method: 'GET',
        headers: {
          Authorization: 'Basic ' + btoa(':' + 'maxai'),
        },
      });
  
      if(response.status == 200)
      {
      const text = await response.text();
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(text, 'text/xml');
      const x = xmlDoc.getElementsByTagName('info');
      let filename = null;
      d.state = xmlDoc.querySelector('state').textContent;
      d.volume = xmlDoc.querySelector('volume').textContent;
      d.srcPosition = xmlDoc.querySelector('time').textContent;
      d.srcMax = xmlDoc.querySelector('length').textContent;

      for (let i = 0; i < x.length; i++) {
        const name = x[i].getAttribute('name');
        const text = x[i].textContent;
  
        switch (name) {
          case 'title':
            d.name = text;
            break;
          case 'artist':
            d.artist = text;
            break;
          case 'artwork_url':
            d.artwork = text;
            break;
          case 'filename':
            filename = text.split('.')[0];
            break;
          default:
            break;
        }
      }
    }
    } catch (error) {
    }

    return d;
  }  

async  function mediaControl(msg) {
    console.log(msg); 
    try {
        const uri = `http://127.0.0.1:8080/requests/status.xml?command=${msg}`;
        const response = await fetch(uri, {
            method: 'GET',
            headers: {
                'Authorization': 'Basic ' + btoa(':maxai')
            }
        });
      
      setTimeout(async () =>{
      const data = await getCurrentSong();
      updateSongData(data);
      }, 100);
    } catch (error) {
    }
}

async function updateSongData(data)
{

    document.getElementById("sartist").textContent = data.artist;
    document.getElementById("sname").textContent = data.name;
    document.getElementById("sartwork").src = data.artwork;
    document.getElementById("soundSlider").value = data.volume;
    document.getElementById("sourceSlider").max = data.srcMax;
    document.getElementById("sourceSlider").value = data.srcPosition;

    if(data.state == "paused")
    {
      document.getElementById("playButton").src = "images/play.svg"
    }
    else
    {
      document.getElementById("playButton").src = "images/pause.svg"
    }

    if(data.volume == 0)
    {
      document.getElementById("volumeButton").src = "images/volume-mute.svg"
    }
    else if(data.volume > 128)
    {
      document.getElementById("volumeButton").src = "images/player-volume.svg"
    }
    else{
      document.getElementById("volumeButton").src = "images/volume-min.svg"
    }

}

const refresh = document.getElementById("refreshBTN");
refresh.addEventListener('click', async () => {
    const data = await getCurrentSong();
    updateSongData(data);
})

const playButton = document.getElementById("playButton");
playButton.addEventListener('click', async () => {
  mediaControl("pl_pause");
})

const prevButton = document.getElementById("prevButton");
prevButton.addEventListener('click', async () => {
  mediaControl("pl_previous");
})

const nextButton = document.getElementById("nextButton");
nextButton.addEventListener('click', async () => {
  mediaControl("pl_next");
})

let isSoundDragging = false;
const soundSlider = document.getElementById("soundSlider");
soundSlider.addEventListener('input', () =>{
  isSoundDragging = true;
})

soundSlider.addEventListener('change', async () => {
  const val = soundSlider.value;
  await mediaControl(`volume&val=${val}`);
  isSoundDragging = false;
});


const sourceSlider = document.getElementById("sourceSlider");
sourceSlider.addEventListener('change', async ()=> {
  const val = sourceSlider.value;
  await mediaControl(`seek&val=${val}`);
})

const volumeButton =  document.getElementById("volumeButton");
volumeButton.addEventListener("click", async () =>
{
  const soundSlider = document.getElementById("soundSlider");
  if(soundSlider.value > 0)
  {
    volumeButton.src = "images/volume-mute.svg";
    soundSlider.value = 0;
    await mediaControl(`volume&val=0`);
    isSoundDragging = false;
  }
})

document.addEventListener('keydown',async function(event) {
  if (event.key === ' ') {
    await mediaControl('pl_pause');
    event.preventDefault();
  }
});


updateSongData();
setInterval( async () => {
  if(!isSoundDragging)
  {
    const data = await getCurrentSong();
    updateSongData(data);
  }
}, 1000);