// State management
const state = {
    characters: [],
    scenes: Array(4).fill(null).map(() => ({
        sceneDescription: '',
        characterStates: {},
        objectsBackground: ''
    })),
    layoutRef: null,
    aspectRatio: '3:4',
    lastThoughtProcess: '',
    availableCharacterFiles: [],
    availableLayoutFiles: []
};

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await loadReferenceFiles();
    setupEventListeners();
    renderScenes();
}

// Load reference files from server
async function loadReferenceFiles() {
    try {
        const [layoutFiles, characterFiles] = await Promise.all([
            fetch('/api/files/layout').then(res => res.json()),
            fetch('/api/files/characters').then(res => res.json())
        ]);

        state.availableLayoutFiles = layoutFiles.files;
        state.availableCharacterFiles = characterFiles.files;

        populateFileSelect('layoutRefSelect', layoutFiles.files);
    } catch (error) {
        console.error('Failed to load reference files:', error);
    }
}

function populateFileSelect(selectId, files) {
    const select = document.getElementById(selectId);
    files.forEach(file => {
        const option = document.createElement('option');
        option.value = file;
        option.textContent = file;
        select.appendChild(option);
    });
}

// Event listeners
function setupEventListeners() {
    // Aspect ratio is fixed to 3:4 - no event listener needed

    document.getElementById('addCharacterBtn').addEventListener('click', addCharacter);
    document.getElementById('generateBtn').addEventListener('click', generateImage);
    document.getElementById('retryFromThoughtBtn')?.addEventListener('click', () => generateImage(true));
    document.getElementById('retryImageOnlyBtn')?.addEventListener('click', () => generateImage(false, true));
}

// Character management
function addCharacter() {
    const character = {
        id: Date.now(),
        name: '',
        refImage: ''
    };

    state.characters = [...state.characters, character];
    renderCharacters();
    renderScenes();
}

function removeCharacter(id) {
    state.characters = state.characters.filter(char => char.id !== id);
    renderCharacters();
    renderScenes();
}

function renderCharacters() {
    const container = document.getElementById('charactersList');
    container.innerHTML = '';

    state.characters.forEach((character, index) => {
        const div = document.createElement('div');
        div.className = 'character-item';

        // Build options for character reference select
        let refImageOptions = '<option value="">-- Select from existing --</option>';
        state.availableCharacterFiles.forEach(file => {
            const selected = character.refImage === file ? 'selected' : '';
            refImageOptions += `<option value="${file}" ${selected}>${file}</option>`;
        });

        div.innerHTML = `
            <div class="form-group">
                <label>Character ${index + 1} Name:</label>
                <input type="text"
                       data-char-id="${character.id}"
                       data-field="name"
                       value="${character.name}"
                       placeholder="Enter character name">
            </div>
            <div class="form-group">
                <label>Reference Image:</label>
                <select data-char-id="${character.id}"
                        data-field="refImage">
                    ${refImageOptions}
                </select>
            </div>
            <button type="button" class="remove-btn" data-char-id="${character.id}">Remove</button>
        `;
        container.appendChild(div);
    });

    // Add event listeners
    container.querySelectorAll('input[data-field="name"]').forEach(input => {
        input.addEventListener('input', (e) => {
            const charId = parseInt(e.target.dataset.charId);
            const char = state.characters.find(c => c.id === charId);
            if (char) {
                char.name = e.target.value;
                renderScenes();
            }
        });
    });

    container.querySelectorAll('select[data-field="refImage"]').forEach(select => {
        select.addEventListener('change', (e) => {
            const charId = parseInt(e.target.dataset.charId);
            const char = state.characters.find(c => c.id === charId);
            if (char) {
                char.refImage = e.target.value;
            }
        });
    });

    container.querySelectorAll('button.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const charId = parseInt(e.target.dataset.charId);
            removeCharacter(charId);
        });
    });
}

// Scene management
function renderScenes() {
    const container = document.getElementById('scenesContainer');
    container.innerHTML = '';

    state.scenes.forEach((scene, index) => {
        const div = document.createElement('div');
        div.className = 'scene-panel';

        let characterStatesHTML = '';
        state.characters.forEach(char => {
            characterStatesHTML += `
                <div class="character-state">
                    <label>${char.name || 'Unnamed Character'}:</label>
                    <input type="text"
                           data-scene="${index}"
                           data-char-id="${char.id}"
                           value="${scene.characterStates[char.id] || ''}"
                           placeholder="Describe character state">
                </div>
            `;
        });

        div.innerHTML = `
            <h4>Panel ${index + 1}</h4>
            <div class="form-group">
                <label>Scene Description:</label>
                <textarea data-scene="${index}" data-field="sceneDescription">${scene.sceneDescription}</textarea>
            </div>
            ${characterStatesHTML}
            <div class="form-group">
                <label>Objects & Background:</label>
                <textarea data-scene="${index}" data-field="objectsBackground">${scene.objectsBackground}</textarea>
            </div>
        `;
        container.appendChild(div);
    });

    // Add event listeners
    container.querySelectorAll('textarea[data-field="sceneDescription"]').forEach(textarea => {
        textarea.addEventListener('input', (e) => {
            const sceneIndex = parseInt(e.target.dataset.scene);
            state.scenes[sceneIndex] = {
                ...state.scenes[sceneIndex],
                sceneDescription: e.target.value
            };
        });
    });

    container.querySelectorAll('textarea[data-field="objectsBackground"]').forEach(textarea => {
        textarea.addEventListener('input', (e) => {
            const sceneIndex = parseInt(e.target.dataset.scene);
            state.scenes[sceneIndex] = {
                ...state.scenes[sceneIndex],
                objectsBackground: e.target.value
            };
        });
    });

    container.querySelectorAll('input[data-char-id]').forEach(input => {
        input.addEventListener('input', (e) => {
            const sceneIndex = parseInt(e.target.dataset.scene);
            const charId = parseInt(e.target.dataset.charId);
            state.scenes[sceneIndex] = {
                ...state.scenes[sceneIndex],
                characterStates: {
                    ...state.scenes[sceneIndex].characterStates,
                    [charId]: e.target.value
                }
            };
        });
    });
}

// Image generation
async function generateImage(retryFromThought = false, retryImageOnly = false) {
    showLoading(true);
    hideResults();

    try {
        const requestData = {
            aspect_ratio: state.aspectRatio,
            layout_ref_image: state.layoutRef,
            characters: state.characters.map(char => ({
                name: char.name,
                ref_image: char.refImage || '',
                description: ''
            })),
            scenes: state.scenes.map(scene => ({
                scene_description: scene.sceneDescription,
                character_states: scene.characterStates,
                objects_background: scene.objectsBackground
            }))
        };

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (result.success) {
            state.lastThoughtProcess = result.thought_process;
            displayResults(result);
        } else {
            displayError(result.error || 'Generation failed');
        }
    } catch (error) {
        displayError(`Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// UI updates
function showLoading(show) {
    const loadingState = document.getElementById('loadingState');
    if (show) {
        loadingState.classList.remove('hidden');
    } else {
        loadingState.classList.add('hidden');
    }
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('generatedImageContainer').classList.add('hidden');
    document.getElementById('errorMessage').classList.add('hidden');
}

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const imageContainer = document.getElementById('generatedImageContainer');
    const thoughtContent = document.getElementById('thoughtProcessContent');
    const generatedImage = document.getElementById('generatedImage');
    const downloadBtn = document.getElementById('downloadBtn');

    thoughtContent.textContent = result.thought_process;

    if (result.image_url) {
        generatedImage.src = result.image_url;
        downloadBtn.href = result.image_url;
        imageContainer.classList.remove('hidden');
    }

    resultsSection.classList.remove('hidden');
}

function displayError(message) {
    const resultsSection = document.getElementById('resultsSection');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    resultsSection.classList.remove('hidden');
}
