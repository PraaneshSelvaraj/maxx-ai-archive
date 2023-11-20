function populateVoiceDropdown() {
	const engineDropdown = document.getElementById('engineDropdown');
	const voiceDropdown = document.getElementById('voiceDropdown');
	
	const endpointUrl = 'https://api.wit.ai/voices?v=20220622';
	
	const token = '2OFLJ2ZSMDBDYPRR54FICKTG3BLMYK5Z';
	if (engineDropdown.value === 'Wit.AI') {
		voiceDropdown.innerHTML='';
		fetch(endpointUrl, {
			headers: {
				"Authorization": `Bearer ${token}`
			}
		})
		.then(response => response.json())
		.then(data => {
			voiceDropdown.innerHTML = '';

			for (const locale in data) {
				if (data.hasOwnProperty(locale)) {
					const voices = data[locale];
					voices.forEach(voice => {
						const option = document.createElement('option');
						option.value = voice.name;
						option.textContent = voice.name;
						voiceDropdown.appendChild(option);
					});
				}
			}
		})
		.catch(error => {
			console.error('Error fetching data:', error);
		});
	} 
	else if (engineDropdown.value == 'GTTS')
	{
		const gttsVoiceOptions = {
			'India' : 'co.in',
			'Australia' : 'com.au',
			'United Kingdom':'co.uk',
			'Canada':'ca',
			'United States':'us',
			'Ireland':'ie',
			'South Africa':'co.za',
		};
		voiceDropdown.innerHTML = '';
		for (const optionText in gttsVoiceOptions) {
			if (gttsVoiceOptions.hasOwnProperty(optionText)) {
				const optionValue = gttsVoiceOptions[optionText];
				const option = document.createElement('option');
				option.value = optionValue;
				option.textContent = optionText;
				voiceDropdown.appendChild(option);
			}
		}
	}
	
	else {
		voiceDropdown.innerHTML = '';
	}
}


function synthesizeWITAudio(txt, userConfig) {
	const witAccessToken = '2OFLJ2ZSMDBDYPRR54FICKTG3BLMYK5Z';
	const witApiUrl = 'https://api.wit.ai/synthesize';
	const version = '20220622'; 


	const audio = new Audio();

	return fetch(`${witApiUrl}?v=${version}`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${witAccessToken}`,
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			q: txt,
			voice: userConfig.defaults.voice,
		}),
	})
	.then((response) => {
		if (!response.ok) {
			throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
		}
		return response.blob();
	})
	.then((audioBlob) => {
		audio.src = URL.createObjectURL(audioBlob);

		audio.play();

		return 'Audio is playing.';
	})
	.catch((error) => {
		return `Error: ${error.message}`;
	});
}

function setVoice()
{
	const engine = document.getElementById("engineDropdown").value;
	const voice = document.getElementById("voiceDropdown").value;
	console.log(engine);
	console.log(voice);
	let filePath;
	api.getConfigFile()
		.then((path) => {
			filePath = path; 
			console.log(filePath);
			fetch(filePath)
				.then((response) => {
					if (!response.ok) {
					throw new Error(`Failed to fetch JSON file: ${response.statusText}`);
					}
					return response.json();
				})
					.then((jsonData) => {
						console.log(jsonData);
						if(engine == "Wit.AI")
							{
								jsonData.defaults.voice_engine = "wit.ai";
							}
						else if(engine=="GTTS")
							{
								jsonData.defaults.voice_engine = "gTTS";
							}
						jsonData.defaults.voice = voice;
						api.updateJsonFile(jsonData)	
						alert("Engine and Voice has been changed successfully.");		
					})
				.catch((error) => {
					console.error("Error loading JSON file:", error);
				});
		})

	
	

}
document.addEventListener('DOMContentLoaded', populateVoiceDropdown);

const engineDropdown = document.getElementById('engineDropdown');
engineDropdown.addEventListener('change', populateVoiceDropdown);

const set_voice_btn = document.getElementById('select_button');
set_voice_btn.addEventListener('click', setVoice);

const synthesizeButton = document.getElementById('test_button');

synthesizeButton.addEventListener('click', function () {
	const userConfig = {
		defaults: {
			voice: document.getElementById('voiceDropdown').value,
		},
	};

	const txt = document.getElementById("voicetext").value;
	const engine = document.getElementById("engineDropdown").value;
	if(engine == "Wit.AI" && txt != ""){
	synthesizeWITAudio(txt, userConfig)
		.then((result) => {
			console.log(result);
		})
		.catch((error) => {
			console.error(error);
		});
	}
});