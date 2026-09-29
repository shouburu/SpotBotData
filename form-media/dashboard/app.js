'use strict';

const formatNames = { text: 'Text guidance', image: 'Still image', animation: 'Animated diagram', video: 'Short video', external: 'External reference' };
const statusNames = { pending: 'Pending', accepted: 'Accepted', rejected: 'Rejected', 'needs-review': 'Needs review' };
const recommendationNames = { provisional: 'Provisional recommendation', reviewed: 'Teaching format reviewed', 'pilot-reviewed': 'Teaching format reviewed for the pilot' };
const ui = {
  data: null, selectedId: null, scope: 'pilot', search: '', activity: '', format: '', status: '', generatedRound: '', round: null,
  drafts: new Map(), previews: new Map(), comparisons: new Map(), overlays: new Map(), saving: new Set(), loading: false,
};
const $ = id => document.getElementById(id);
const list = value => Array.isArray(value) ? value : [];
const text = value => value == null ? '' : String(value);
const titleCase = value => text(value).replace(/[_-]/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
const number = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) ? Number(value) : null;
const fmtNumber = value => new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
const fmtBytes = value => {
  const bytes = number(value);
  if (bytes === null) return 'Size not measured';
  return bytes >= 1000000 ? `${fmtNumber(bytes / 1000000)} MB` : `${fmtNumber(bytes / 1000)} KB`;
};

function node(tag, attrs = {}, children = []) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === 'class') element.className = value;
    else if (key === 'on') Object.entries(value).forEach(([event, callback]) => element.addEventListener(event, callback));
    else if (key === 'value') element.value = value;
    else if (key === 'checked' || key === 'disabled' || key === 'hidden') element[key] = Boolean(value);
    else element.setAttribute(key, value === true ? '' : text(value));
  }
  for (const child of (Array.isArray(children) ? children : [children])) {
    if (child !== null && child !== undefined && child !== false) element.append(child instanceof Node ? child : document.createTextNode(text(child)));
  }
  return element;
}

function icon(kind) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', '20');
  svg.setAttribute('height', '20');
  svg.setAttribute('aria-hidden', 'true');
  const paths = {
    previous: ['m14 6-6 6 6 6'], next: ['m10 6 6 6-6 6'],
    external: ['M14 4h6v6', 'm20 4-9 9', 'M10 4H5a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5'],
    guidance: ['M5 4h14v16H5z', 'M8 8h8', 'M8 12h8', 'M8 16h5'],
    media: ['M4 5h16v14H4z', 'm4 16 5-5 4 4 3-3 4 4', 'M15 9h.01'],
  };
  for (const d of paths[kind] || paths.media) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d); svg.append(path);
  }
  return svg;
}

function announce(message) { $('announcement').textContent = message; }
function currentExercise() { return ui.data?.exercises.find(exercise => exercise.id === ui.selectedId); }
function exerciseAssets(id) { return list(ui.data?.assets).filter(asset => asset.exerciseId === id); }
// Review readiness is derived from delivered media, independently of the saved decision.
function isReleasedForReview(asset) {
  const round = list(ui.data?.rounds).find(item => item.id === assetRoundId(asset));
  return !round?.requiresEditorialPass || asset.reviewStatus === 'accepted'
    || asset.operatorRequestedEdit === true
    || ['candidate', 'accepted'].includes(asset.editorialReview?.status);
}
function reviewMedia(exercise) {
  const kinds = exercise.teachingFormat === 'video' ? ['video', 'external']
    : exercise.teachingFormat === 'external' ? ['external'] : ['image', 'animation', 'video', 'external'];
  return exerciseAssets(exercise.id).filter(asset => kinds.includes(asset.kind) && isReleasedForReview(asset));
}
function newReviewMedia(exercise) {
  if (Array.isArray(exercise.reviewedAssetIds)) return reviewMedia(exercise).filter(asset => !exercise.reviewedAssetIds.includes(asset.id));
  const reviewed = Date.parse(exercise.reviewedAt || '') || 0;
  return reviewMedia(exercise).filter(asset => (Date.parse(asset.createdAt || '') || 0) > reviewed);
}
function queueStatus(exercise) {
  if (newReviewMedia(exercise).length) return 'needs-review';
  return statusNames[exercise.reviewStatus] ? exercise.reviewStatus : 'pending';
}
function mediaUpdateLabel(exercise) {
  const media = reviewMedia(exercise).slice().sort((a, b) => text(b.createdAt).localeCompare(text(a.createdAt)));
  if (!media.length) return exercise.teachingFormat === 'text' ? 'Text guidance' : 'Awaiting media';
  return `${newReviewMedia(exercise).length ? 'New · ' : ''}${roundLabel(assetRoundId(media[0]))} · ${media[0].kind === 'video' ? 'Video ready' : 'Media ready'}`;
}
function exerciseAttempts(id) { return list(ui.data?.attempts).filter(attempt => attempt.exerciseId === id); }
function visibleInRound(asset, exercise) {
  return !ui.round || assetRoundId(asset) === ui.round
    || (ui.round === activeRoundId() && draftFor(exercise).selectedAssetIds.includes(asset.id));
}
function activeRoundId() { return ui.data?.activeRoundId || 'round-1'; }
function assetRoundId(asset) { return asset.roundId || 'round-1'; }
function roundLabel(id) {
  const round = list(ui.data?.rounds).find(item => item.id === id);
  return round?.title?.split('·')[0].trim() || titleCase(id);
}
function assetEdition(asset) { return `${roundLabel(assetRoundId(asset))} · ${asset.styleLabel || titleCase(asset.styleId) || 'Original style'}`; }
function pilotExercises() {
  const round = list(ui.data?.rounds).find(item => item.id === activeRoundId());
  return list(ui.data?.exercises).filter(exercise => Array.isArray(round?.exerciseIds) ? round.exerciseIds.includes(exercise.id) : exercise.pilot);
}
function exerciseHistory(id) {
  const entries = list(ui.data?.reviewHistory).filter(entry => entry.exerciseId === id).slice();
  const previous = ui.data?.exercises.find(exercise => exercise.id === id)?.previousRoundReview;
  if (previous && !entries.some(entry => entry.roundId === previous.roundId && entry.createdAt === previous.reviewedAt)) {
    entries.push({ ...previous, exerciseId: id, createdAt: previous.reviewedAt, source: 'previous-round' });
  }
  return entries.sort((a, b) => text(b.createdAt).localeCompare(text(a.createdAt)));
}
function draftFor(exercise) {
  const key = `${activeRoundId()}:${exercise.id}`;
  if (!ui.drafts.has(key)) ui.drafts.set(key, {
    roundId: activeRoundId(),
    reviewStatus: queueStatus(exercise),
    notes: text(exercise.notes), selectedAssetIds: [...list(exercise.selectedAssetIds)], dirty: false,
  });
  return ui.drafts.get(key);
}

function dirty(exercise) {
  const draft = draftFor(exercise);
  draft.dirty = true;
  if (ui.selectedId === exercise.id) {
    const feedback = $('review-feedback');
    if (feedback) { feedback.textContent = 'Unsaved review'; feedback.className = 'review-feedback'; }
    const save = $('save-review');
    if (save) save.disabled = ui.saving.has(exercise.id);
  }
}

function safeMediaUrl(value) {
  if (typeof value !== 'string' || !value) return null;
  try {
    const url = new URL(value, location.origin);
    if (url.origin !== location.origin || !['http:', 'https:'].includes(url.protocol)) return null;
    if (!url.pathname.startsWith('/assets/') && !url.pathname.startsWith('/diagrams/')) return null;
    return url.href;
  } catch { return null; }
}

function safeExternalUrl(value) {
  try { const url = new URL(value); return url.protocol === 'https:' ? url.href : null; } catch { return null; }
}

function youtubeEmbedUrl(value) {
  try {
    const source = new URL(value);
    if (source.protocol !== 'https:') return null;
    const host = source.hostname.toLowerCase();
    const parts = source.pathname.split('/').filter(Boolean);
    const id = host === 'youtu.be' ? parts[0]
      : ['youtube.com', 'www.youtube.com', 'm.youtube.com', 'www.youtube-nocookie.com'].includes(host)
        ? (source.pathname === '/watch' ? source.searchParams.get('v') : ['shorts', 'embed'].includes(parts[0]) ? parts[1] : null)
        : null;
    if (!/^[A-Za-z0-9_-]{11}$/.test(id || '')) return null;
    const url = new URL(`https://www.youtube-nocookie.com/embed/${id}`);
    url.searchParams.set('playsinline', '1');
    url.searchParams.set('rel', '0');
    url.searchParams.set('origin', location.origin);
    const time = source.searchParams.get('start') || source.searchParams.get('t') || '';
    const match = /^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/.exec(time);
    const start = /^\d+$/.test(time) ? Number(time) : match ? Number(match[1] || 0) * 3600 + Number(match[2] || 0) * 60 + Number(match[3] || 0) : 0;
    if (start > 0) url.searchParams.set('start', String(start));
    return url.href;
  } catch { return null; }
}

function filteredExercises() {
  const pilotIds = new Set(pilotExercises().map(exercise => exercise.id));
  return list(ui.data?.exercises).filter(exercise => {
    if (ui.scope === 'pilot' && !pilotIds.has(exercise.id)) return false;
    if (ui.activity && !list(exercise.metadata?.activities).includes(ui.activity)) return false;
    if (ui.format && exercise.teachingFormat !== ui.format) return false;
    if (ui.status && queueStatus(exercise) !== ui.status) return false;
    if (ui.generatedRound && !reviewMedia(exercise).some(asset => assetRoundId(asset) === ui.generatedRound)) return false;
    const searchable = [exercise.name, exercise.muscle_group, exercise.bodyPosition, exercise.compound === true ? 'compound' : '', ...list(exercise.metadata?.equipment), ...list(exercise.metadata?.aliases), ...list(exercise.metadata?.primaryMuscles), ...list(exercise.metadata?.secondaryMuscles)].join(' ').toLocaleLowerCase();
    return ui.search.toLocaleLowerCase().split(/\s+/).filter(Boolean).every(term => searchable.includes(term));
  }).sort((a, b) => (ui.scope === 'pilot' ? (number(a.priority) ?? 99) - (number(b.priority) ?? 99) : 0) || a.name.localeCompare(b.name));
}

function renderSummary() {
  const exercises = ui.data.exercises;
  const pilots = pilotExercises();
  const pilotAccepted = pilots.filter(exercise => exercise.reviewStatus === 'accepted').length;
  const drafted = pilots.filter(exercise => reviewMedia(exercise).some(asset => assetRoundId(asset) === activeRoundId())).length;
  const videoCandidates = pilots.filter(exercise => list(ui.data.assets).some(asset =>
    asset.exerciseId === exercise.id && assetRoundId(asset) === activeRoundId() && asset.kind === 'video'
    && isUnflaggedCandidate(asset) && ['candidate', 'accepted'].includes(asset.editorialReview?.status))).length;
  const videoProgress = pilots.length && pilots.every(exercise => exercise.teachingFormat === 'video')
    ? `${videoCandidates} have AI-reviewed video candidates · ` : '';
  $('queue-progress').replaceChildren(
    node('strong', {}, `${exercises.filter(exercise => queueStatus(exercise) === 'needs-review').length} need review across catalog · ${roundLabel(activeRoundId())}: ${drafted} of ${pilots.length} have new review media`),
    node('span', {}, `${videoProgress}${pilotAccepted} accepted or carried forward · ${exercises.length} catalog exercises tracked · Earlier reviews retained`),
  );
  const budget = ui.data.budget || {};
  const limit = number(budget.limit), spent = number(budget.spent), reserved = number(budget.reserved), remaining = number(budget.remaining);
  if (limit === null) { $('budget').replaceChildren(node('span', { class: 'subtle' }, 'Credit balance unavailable')); return; }
  const meter = node('div', { class: 'budget-bar', 'aria-hidden': 'true' });
  const spentBar = node('span', { class: 'budget-spent' });
  const reservedBar = node('span', { class: 'budget-reserved' });
  spentBar.style.width = `${Math.min(100, Math.max(0, (spent ?? 0) / Math.max(limit, 1) * 100))}%`;
  reservedBar.style.width = `${Math.min(100, Math.max(0, (reserved ?? 0) / Math.max(limit, 1) * 100))}%`;
  meter.append(spentBar, reservedBar);
  $('budget').replaceChildren(meter, node('div', { class: 'budget-text' }, [
    node('strong', {}, `${remaining === null ? '—' : fmtNumber(remaining)} / ${fmtNumber(limit)} ${budget.periodId ? 'period' : 'pilot'} credits available`),
    node('span', { class: 'subtle' }, `${spent === null ? 'Unknown' : fmtNumber(spent)} spent${budget.periodId ? ' this period' : ''} · ${reserved === null ? 'Unknown' : fmtNumber(reserved)} reserved${budget.periodId && number(budget.lifetimeSpent) !== null ? ` · ${fmtNumber(budget.lifetimeSpent)} lifetime` : ''}`),
  ]));
  $('catalog-version').textContent = `Catalog ${text(ui.data.catalog?.version)} · revision ${text(ui.data.catalog?.revision)}`;
}

function renderList() {
  const exercises = filteredExercises();
  $('result-count').textContent = fmtNumber(exercises.length);
  $('mobile-result-count').textContent = `${exercises.length} ${ui.scope === 'pilot' ? 'in pilot' : 'results'}`;
  const filterCount = [ui.activity, ui.format, ui.status, ui.generatedRound].filter(Boolean).length;
  $('active-filter-count').textContent = filterCount ? `(${filterCount})` : '';
  $('scope-pilot').setAttribute('aria-pressed', String(ui.scope === 'pilot'));
  $('scope-pilot').textContent = `${roundLabel(activeRoundId())} pilot`;
  $('scope-all').setAttribute('aria-pressed', String(ui.scope === 'all'));
  const fragment = document.createDocumentFragment();
  for (const exercise of exercises) {
    const reviewStatus = queueStatus(exercise);
    fragment.append(node('button', {
      type: 'button', class: 'exercise-row', 'aria-current': String(exercise.id === ui.selectedId),
      'aria-label': `${exercise.name}, ${formatNames[exercise.teachingFormat] || 'Unclassified'}, ${statusNames[reviewStatus]}`,
      on: { click: () => selectExercise(exercise.id, true) },
    }, [
      node('span', { class: 'row-copy' }, [node('span', { class: 'row-title' }, exercise.name), node('span', { class: 'row-caption' }, mediaUpdateLabel(exercise))]),
      node('span', { class: `row-status ${reviewStatus}` }, statusNames[reviewStatus]),
    ]));
  }
  if (!exercises.length) fragment.append(node('div', { class: 'empty-results' }, [node('strong', {}, 'No matching exercises'), node('p', {}, 'Try another search or clear the filters.'), node('button', { type: 'button', class: 'text-button', on: { click: clearFilters } }, 'Clear search and filters')]));
  $('exercise-list').replaceChildren(fragment);
  $('exercise-list').setAttribute('aria-busy', 'false');
  return exercises;
}

function setCatalogOpen(open) {
  document.querySelector('.catalog-panel').classList.toggle('is-open', open);
  $('catalog-toggle').setAttribute('aria-expanded', String(open));
}

function selectExercise(id, focus = false) {
  ui.selectedId = id;
  const selected = currentExercise();
  if (selected && ui.round && !reviewMedia(selected).some(asset => assetRoundId(asset) === ui.round)) ui.round = '';
  syncExerciseHash();
  renderList(); renderDetail();
  if (matchMedia('(max-width: 720px)').matches) {
    setCatalogOpen(false);
    if (focus) { $('exercise-detail').focus({ preventScroll: true }); $('exercise-detail').scrollIntoView({ block: 'start' }); }
  }
}

function syncExerciseHash() {
  const hash = ui.selectedId ? `#${encodeURIComponent(ui.selectedId)}` : '';
  if (location.hash !== hash) history.replaceState(null, '', `${location.pathname}${location.search}${hash}`);
}

function navigateToHash() {
  if (!ui.data) return;
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const exercise = ui.data.exercises.find(row => row.id === id);
  // Non-exercise anchors, including the skip link, retain their native behavior.
  if (!exercise) return;
  if (!exercise.pilot) ui.scope = 'all';
  const filtersChanged = !filteredExercises().some(row => row.id === id);
  if (filtersChanged) resetFilterValues();
  selectExercise(id, true);
  announce(`${exercise.name} opened.${filtersChanged ? ' Conflicting filters were cleared.' : ''}`);
}

function applyFilters() {
  const exercises = renderList();
  if (!exercises.some(exercise => exercise.id === ui.selectedId)) ui.selectedId = exercises[0]?.id || null;
  syncExerciseHash();
  renderList(); renderDetail();
}

function resetFilterValues() {
  ui.generatedRound = ''; $('filter-generated-round').value = '';
  ui.search = ''; ui.activity = ''; ui.format = ''; ui.status = '';
  $('search').value = ''; $('filter-activity').value = ''; $('filter-format').value = ''; $('filter-status').value = '';
}

function clearFilters() {
  resetFilterValues();
  applyFilters();
}

function isUnflaggedCandidate(asset) {
  return asset.reviewStatus !== 'rejected'
    && !['rejected', 'needs-review', 'needs-correction'].includes(asset.editorialReview?.status)
    && !['rejected', 'needs-review'].includes(asset.trainerReview?.status);
}

function newestCandidate(assets) {
  const unflagged = assets.filter(isUnflaggedCandidate);
  const candidates = unflagged.length ? unflagged : assets;
  // Equal or missing timestamps fall back to the later registration order.
  return candidates.reduce((latest, asset) => !latest
    || (Date.parse(asset.createdAt) || 0) >= (Date.parse(latest.createdAt) || 0) ? asset : latest, null);
}

function defaultAsset(exercise, assets) {
  // Failed or unscreened gated-round drafts remain selectable in Versions,
  // but are not the automatic teaching preview.
  assets = assets.filter(isReleasedForReview);
  const current = assets.filter(asset => assetRoundId(asset) === activeRoundId());
  const selected = draftFor(exercise).selectedAssetIds.map(id => assets.find(asset => asset.id === id)).filter(Boolean);
  const selectedCurrent = selected.filter(asset => assetRoundId(asset) === activeRoundId());
  if (exercise.teachingFormat === 'text' && !selected.length) return null;
  const preferredKind = exercise.teachingFormat === 'external' ? 'external' : exercise.teachingFormat === 'video' ? 'video' : 'image';
  const fresh = newReviewMedia(exercise).filter(asset => assets.some(visible => visible.id === asset.id));
  // This is an operator review screen: a flagged new video must remain discoverable.
  // Previewing it does not select or approve it for the exercise.
  const newMedia = newestCandidate(fresh.filter(asset => asset.kind === preferredKind)) || newestCandidate(fresh);
  if (newMedia) return newMedia;
  const unflagged = current.filter(isUnflaggedCandidate);
  const reviewed = unflagged.filter(asset =>
    [asset.editorialReview?.status, asset.trainerReview?.status].some(status => ['candidate', 'accepted'].includes(status))
    && !(asset.kind === 'image' && asset.presentationRole !== 'static-detail' && /-start(?:-still)?$/.test(asset.shot || '')));
  return selectedCurrent.find(asset => asset.kind === preferredKind) || selectedCurrent[0]
    || selected.find(asset => asset.kind === preferredKind) || selected[0]
    || newestCandidate(reviewed.filter(asset => asset.kind === preferredKind)) || newestCandidate(reviewed)
    || newestCandidate(unflagged.filter(asset => asset.kind === preferredKind))
    || newestCandidate(current.filter(asset => asset.kind === preferredKind))
    || newestCandidate(unflagged)
    || newestCandidate(current.filter(asset => asset.kind === 'image')) || newestCandidate(current)
    || newestCandidate(assets.filter(asset => asset.kind === preferredKind))
    || newestCandidate(assets.filter(asset => asset.kind === 'image')) || newestCandidate(assets);
}

function previewAsset(exercise, assets) {
  return assets.find(asset => asset.id === ui.previews.get(exercise.id)) || defaultAsset(exercise, assets);
}

function candidateGroupKey(asset) {
  return [assetRoundId(asset), asset.styleId || '', asset.kind, asset.shot || asset.title || asset.id].join(':');
}

function candidateTitle(asset, assets) {
  const peers = assets.filter(item => candidateGroupKey(item) === candidateGroupKey(asset) && Boolean(item.edit) === Boolean(asset.edit))
    .sort((a, b) => (Date.parse(a.createdAt) || 0) - (Date.parse(b.createdAt) || 0));
  const take = asset.edit || peers.length > 1 ? ` · ${asset.edit ? 'Edit' : 'Take'} ${peers.findIndex(item => item.id === asset.id) + 1}` : '';
  return `${asset.title || asset.id}${take}`;
}

function assetFacts(asset) {
  if (!asset) return null;
  const external = asset.kind === 'external';
  const facts = external ? [] : [fmtBytes(asset.bytes)];
  if (number(asset.width) > 0 && number(asset.height) > 0) {
    facts.push(external ? (asset.height > asset.width ? 'Portrait' : asset.width > asset.height ? 'Landscape' : 'Square') : `${asset.width} × ${asset.height}`);
  }
  if (number(asset.durationSeconds) > 0) facts.push(`${fmtNumber(asset.durationSeconds)} seconds${external ? ' · full source' : ''}`);
  if (!facts.length) return null;
  return node('div', { class: 'asset-facts' }, facts.map(fact => node('span', {}, fact)));
}

function mediaPreview(exercise, asset, comparison = false) {
  const preview = node('div', { class: 'phone-preview' });
  preview.append(node('div', { class: 'preview-header' }, [node('span', {}, 'Form guidance'), node('span', { class: 'subtle' }, comparison ? 'Comparison' : 'Phone preview')]));
  if (asset) preview.append(node('div', { class: 'preview-edition' }, assetEdition(asset)));
  if (!asset) {
    const isText = exercise.teachingFormat === 'text';
    const instructions = list(exercise.instructions);
    preview.append(node('div', { class: 'preview-empty' }, [
      icon(isText ? 'guidance' : 'media'),
      node('h3', {}, isText ? 'A clear cue can be enough.' : 'A study is waiting to be made.'),
      node('p', {}, isText ? (instructions[0] || 'Review the written guidance for this exercise.') : `The current recommendation is ${text(formatNames[exercise.teachingFormat] || 'form media').toLowerCase()}. ${ui.round ? `There are no candidates in ${roundLabel(ui.round)} yet.` : 'There are no candidate assets yet.'}`),
    ]));
    preview.append(node('div', { class: 'preview-caption' }, isText ? 'Text-only candidate. The full instructions are alongside this preview.' : 'Candidate media will appear here after generation or registration.'));
    return preview;
  }
  if (asset.kind === 'external') {
    const url = safeExternalUrl(asset.url);
    const embedUrl = youtubeEmbedUrl(asset.url);
    const player = node('div', { class: `youtube-player ${asset.height > asset.width ? 'portrait' : 'landscape'}`, hidden: true });
    const load = embedUrl ? node('button', { type: 'button', class: 'button primary', on: { click: () => {
      const open = player.hidden;
      player.hidden = !open;
      player.replaceChildren(...(open ? [node('iframe', {
        src: embedUrl, title: `${exercise.name} · ${asset.source || 'YouTube reference'}`,
        allow: 'autoplay; encrypted-media; picture-in-picture; fullscreen', allowfullscreen: true,
        referrerpolicy: 'strict-origin-when-cross-origin',
      })] : []));
      load.textContent = open ? 'Close video' : 'Load YouTube video';
    } } }, 'Load YouTube video') : null;
    preview.append(node('div', { class: 'media-stage external-stage' }, [
      icon('external'), node('h3', {}, asset.title || 'Expert reference'),
      node('p', {}, asset.alt || 'Open the reference and compare the demonstration with the exercise instructions.'),
      asset.source ? node('p', { class: 'subtle' }, asset.source) : null,
      load,
      url ? node('a', { href: url, target: '_blank', rel: 'noopener noreferrer', class: 'button secondary' }, ['Open reference', icon('external')]) : node('p', { class: 'media-failure' }, 'This reference needs a valid HTTPS URL.'),
      embedUrl ? node('p', { class: 'subtle' }, 'Play here with YouTube controls. If the player is unavailable, open the publisher reference above.') : null,
    ]));
    if (embedUrl) preview.append(player);
  } else {
    const url = safeMediaUrl(asset.url);
    const stage = node('div', { class: 'media-stage' });
    if (!url) stage.append(node('div', { class: 'media-failure' }, 'The local asset path is unavailable. Register the asset and refresh to try again.'));
    else {
      const onError = () => stage.replaceChildren(node('div', { class: 'media-failure', role: 'status' }, 'This media could not be loaded. Check its local file and refresh. The written guidance remains available.'));
      const path = new URL(url).pathname;
      if (path.startsWith('/diagrams/') && /\.html?$/i.test(path)) {
        stage.append(node('iframe', { src: url, title: asset.title || `${exercise.name} movement diagram`, sandbox: 'allow-scripts', loading: 'lazy', referrerpolicy: 'no-referrer' }));
      } else if (asset.kind === 'video' || /\.(mp4|webm|mov)$/i.test(path)) {
        const video = node('video', { controls: true, playsinline: true, preload: 'none', 'aria-label': asset.alt || asset.title || exercise.name, on: { error: onError } });
        video.muted = true;
        const poster = safeMediaUrl(asset.posterUrl);
        if (poster) video.poster = poster;
        video.src = url;
        stage.append(video);
      } else {
        const composite = node('div', { class: 'image-composite' });
        composite.append(node('img', { src: url, alt: asset.alt || asset.title || `${exercise.name} form reference`, loading: 'lazy', on: { error: onError } }));
        const overlayUrl = safeMediaUrl(asset.overlayUrl);
        if (overlayUrl) composite.append(node('img', { src: overlayUrl, class: 'form-overlay', alt: '', 'aria-hidden': 'true', hidden: ui.overlays.get(asset.id) === false, on: { error: event => {
          event.target.hidden = true;
          preview.append(node('p', { class: 'media-failure', role: 'status' }, 'The form guides could not be loaded. The original image remains visible.'));
        } } }));
        stage.append(composite);
      }
    }
    preview.append(stage);
  }
  if (safeMediaUrl(asset.overlayUrl) && asset.kind === 'image') {
    const overlayControls = node('div', { class: 'overlay-controls' }, node('label', { class: 'candidate-choice' }, [
      node('input', { type: 'checkbox', checked: ui.overlays.get(asset.id) !== false, on: { change: event => {
        ui.overlays.set(asset.id, event.target.checked);
        const overlay = preview.querySelector('.form-overlay');
        if (overlay) overlay.hidden = !event.target.checked;
      } } }), 'Show form guides',
    ]));
    const legend = node('div', { class: 'overlay-legend' });
    for (const entry of list(asset.overlayLegend)) {
      const swatch = node('span', { class: 'legend-swatch', 'aria-hidden': 'true' });
      if (/^#[0-9a-f]{3,8}$/i.test(text(entry.color))) swatch.style.backgroundColor = entry.color;
      legend.append(node('span', { class: 'legend-entry' }, [swatch, entry.label || 'Form guide']));
    }
    if (legend.childNodes.length) overlayControls.append(legend);
    preview.append(overlayControls);
  }
  preview.append(node('div', { class: 'preview-caption' }, asset.alt || asset.title || 'Review this candidate against the exercise instructions.'));
  return preview;
}

function candidateControls(exercise, assets, active, allAssets) {
  if (!allAssets.length) return null;
  const hasCarried = ui.round && assets.some(asset => assetRoundId(asset) !== ui.round);
  const section = node('section', { class: 'candidate-list', 'aria-label': 'Candidate media versions' }, [node('h3', {}, `${assets.length} candidate${assets.length === 1 ? '' : 's'}${ui.round ? ` · ${roundLabel(ui.round)}${hasCarried ? ' + carried selections' : ''}` : ' · All rounds'}`)]);
  if (!assets.length) section.append(node('p', { class: 'subtle' }, 'Choose another candidate round above to see earlier assets. You can also open one for comparison below.'));
  const draft = draftFor(exercise);
  const latestByShot = new Map();
  for (const asset of assets) {
    const key = candidateGroupKey(asset), previous = latestByShot.get(key);
    if (!previous || (Date.parse(asset.createdAt) || 0) >= (Date.parse(previous.createdAt) || 0)) latestByShot.set(key, asset);
  }
  const primaryIds = new Set([...latestByShot.values()]
    .filter(asset => !(asset.kind === 'image' && asset.presentationRole !== 'static-detail' && /-start(?:-still)?$/.test(asset.shot || '')))
    .map(asset => asset.id));
  for (const id of [...draft.selectedAssetIds, active?.id, ui.previews.get(exercise.id), ui.comparisons.get(exercise.id)]) primaryIds.add(id);
  const primary = node('div', { class: 'candidate-primary' });
  const earlier = node('div', { class: 'candidate-earlier' });
  section.append(primary);
  for (const asset of assets) {
    const title = candidateTitle(asset, allAssets);
    const editorial = asset.editorialReview;
    const editorialLabel = editorial ? `${editorial.reviewerType === 'ai' ? 'AI' : 'Editorial'}: ${statusNames[editorial.status] || titleCase(editorial.status) || 'Recorded'}` : null;
    const flagged = ['rejected', 'needs-review', 'needs-correction'].includes(editorial?.status);
    const select = node('input', { type: 'checkbox', checked: draft.selectedAssetIds.includes(asset.id), disabled: ui.saving.has(exercise.id), 'aria-label': `Select ${title} for this exercise`, on: { change: event => {
      draft.selectedAssetIds = event.target.checked ? [...new Set([...draft.selectedAssetIds, asset.id])] : draft.selectedAssetIds.filter(id => id !== asset.id);
      if (event.target.checked && row.parentElement === earlier) primary.append(row);
      dirty(exercise);
      updateSelectionSummary(exercise);
    } } });
    const row = node('div', { class: 'candidate-row' }, [
      node('button', { type: 'button', class: 'candidate-button', 'aria-pressed': String(active?.id === asset.id), on: { click: () => { ui.previews.set(exercise.id, asset.id); renderDetail(); } } }, [
        node('span', { class: 'candidate-name' }, title),
        node('span', { class: 'candidate-edition' }, assetEdition(asset)),
        node('span', { class: 'subtle' }, [
          `${formatNames[asset.kind] || titleCase(asset.kind)}${asset.promptFile && asset.promptVersion ? ` · prompt ${asset.promptVersion}` : asset.version ? ` · v${asset.version}` : ''} · Content: ${statusNames[asset.reviewStatus] || 'Pending'}`,
          editorialLabel && node('span', { class: `candidate-editorial${flagged ? ' flagged' : ''}` }, ` · ${editorialLabel}`),
        ]),
      ]), node('label', { class: 'candidate-choice' }, [select, 'Use asset']),
    ]);
    (primaryIds.has(asset.id) ? primary : earlier).append(row);
  }
  if (earlier.childElementCount) section.append(node('details', { class: 'candidate-archive' }, [
    node('summary', {}, 'Starting frames and earlier attempts'), earlier,
  ]));
  if (allAssets.some(asset => asset.id !== active?.id)) {
    const compareId = ui.comparisons.get(exercise.id) || '';
    const choices = allAssets.filter(asset => asset.id !== active?.id);
    const select = node('select', { 'aria-label': 'Compare another candidate version', on: { change: event => { ui.comparisons.set(exercise.id, event.target.value); renderDetail(); } } }, [node('option', { value: '' }, 'No comparison'), ...choices.map(asset => node('option', { value: asset.id }, `${assetEdition(asset)} · ${candidateTitle(asset, allAssets)}`))]);
    select.value = choices.some(asset => asset.id === compareId) ? compareId : '';
    section.append(node('div', { class: 'comparison-control' }, node('label', {}, ['Compare across rounds and styles', select])));
    const compared = choices.find(asset => asset.id === select.value);
    if (compared) section.append(node('section', { class: 'comparison' }, [node('h3', {}, candidateTitle(compared, allAssets)), mediaPreview(exercise, compared, true), assetFacts(compared)]));
  }
  return section;
}

function reviewForm(exercise) {
  const draft = draftFor(exercise);
  const busy = ui.saving.has(exercise.id);
  const form = node('form', { class: 'review-form', on: { submit: event => { event.preventDefault(); void saveReview(exercise); } } });
  form.append(node('h2', {}, `Review this exercise · ${roundLabel(activeRoundId())}`), node('p', {}, 'Needs review means new media is ready or a decision is deferred. Pending means awaiting media or an initial decision. Each save preserves the previous decision in history.'));
  const choices = node('fieldset', { class: 'review-choices', disabled: busy }, node('legend', {}, 'Decision'));
  const labels = { accepted: 'Accept', 'needs-review': 'Needs review', rejected: 'Reject', pending: 'Pending' };
  for (const [value, label] of Object.entries(labels)) choices.append(node('label', { class: 'review-choice' }, [node('input', { type: 'radio', name: 'review-status', value, checked: draft.reviewStatus === value, on: { change: () => { draft.reviewStatus = value; dirty(exercise); } } }), label]));
  form.append(choices, node('label', { class: 'form-field' }, ['Review notes', node('textarea', {
    id: 'review-notes', rows: 3, maxlength: 10000, placeholder: 'What works, what needs correcting, and which view teaches it best…', value: draft.notes, disabled: busy,
    on: { input: event => { draft.notes = event.target.value; dirty(exercise); } },
  })]), node('p', { id: 'selection-summary', class: 'review-note' }), node('div', { class: 'review-actions' }, [
    node('button', { type: 'submit', id: 'save-review', class: 'button', disabled: busy }, busy ? 'Saving review…' : 'Save review'),
    node('button', { type: 'button', class: 'button secondary', disabled: busy, on: { click: () => nextPending(exercise.id) } }, 'Next needs review'),
  ]), node('p', { id: 'review-feedback', class: 'review-feedback', role: 'status' }, busy ? 'Saving your decision…' : draft.dirty ? 'Unsaved review' : 'Review saved locally only.'));
  return form;
}

function updateSelectionSummary(exercise) {
  const selected = draftFor(exercise).selectedAssetIds;
  const count = selected.length;
  const hiddenCount = ui.round ? exerciseAssets(exercise.id).filter(asset => selected.includes(asset.id) && !visibleInRound(asset, exercise)).length : 0;
  const summary = $('selection-summary');
  if (summary) summary.textContent = count ? `${count} asset${count === 1 ? '' : 's'} selected for Form guidance.${hiddenCount ? ` ${hiddenCount} from another round; choose All rounds above to review the full selection.` : ''}` : 'No assets selected. Written guidance remains available.';
}

function nextPending(id) {
  const rows = filteredExercises();
  const index = rows.findIndex(row => row.id === id);
  const ordered = [...rows.slice(index + 1), ...rows.slice(0, index)];
  const next = ordered.find(row => queueStatus(row) === 'needs-review');
  if (next) selectExercise(next.id, true);
  else { const feedback = $('review-feedback'); if (feedback) feedback.textContent = 'No other exercises need review in this filtered queue.'; announce('No other exercises need review in this filtered queue.'); }
}

async function saveReview(exercise) {
  if (ui.saving.has(exercise.id)) return;
  const draft = draftFor(exercise);
  if (draft.reviewStatus === 'accepted' && exercise.teachingFormat !== 'text' && !draft.selectedAssetIds.length) {
    $('review-feedback').textContent = 'Choose “Use asset” on at least one candidate before accepting this exercise.';
    $('review-feedback').className = 'review-feedback error';
    announce('Select at least one candidate asset before accepting this exercise.');
    return;
  }
  const payload = { exerciseId: exercise.id, roundId: draft.roundId, reviewStatus: draft.reviewStatus, notes: draft.notes, selectedAssetIds: [...draft.selectedAssetIds], reviewedAssetIds: exerciseAssets(exercise.id).map(asset => asset.id) };
  ui.saving.add(exercise.id); renderDetail();
  try {
    const response = await fetch('/api/review', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(text(result.error || result.message) || `The review could not be saved (${response.status}).`);
    const savedStatus = statusNames[result.reviewStatus] ? result.reviewStatus : payload.reviewStatus;
    Object.assign(exercise, payload, {
      reviewStatus: savedStatus,
      reviewedAt: result.reviewedAt,
      reviewedAssetIds: result.reviewedAssetIds,
      recommendationStatus: recommendationNames[result.recommendationStatus] ? result.recommendationStatus : exercise.recommendationStatus,
    });
    draft.reviewStatus = savedStatus; draft.dirty = false;
    for (const asset of exerciseAssets(exercise.id)) if (list(result.changedAssetIds).includes(asset.id)) asset.reviewStatus = savedStatus;
    if (result.historyEntry) ui.data.reviewHistory = [...list(ui.data.reviewHistory), result.historyEntry];
    ui.saving.delete(exercise.id); renderSummary(); renderList();
    if (ui.selectedId === exercise.id) {
      renderDetail(); $('review-feedback').textContent = 'Review saved. Your place in the queue is preserved.'; $('review-feedback').className = 'review-feedback success';
    }
    announce(`${exercise.name}: ${statusNames[savedStatus]} review saved.`);
  } catch (error) {
    ui.saving.delete(exercise.id);
    if (ui.selectedId === exercise.id) {
      renderDetail(); $('review-feedback').textContent = `${error.message || 'Saving failed.'} Your notes are still here; try Save review again.`; $('review-feedback').className = 'review-feedback error';
    }
    announce(`Could not save the review for ${exercise.name}. Your notes are preserved.`);
  }
}

function facts(items) {
  const dl = node('dl', { class: 'fact-list' });
  for (const [label, value] of items) if (value !== null && value !== undefined && value !== '') dl.append(node('dt', {}, label), node('dd', {}, value));
  return dl;
}

function disclosure(title, content, open = false) {
  return node('details', { class: 'disclosure', open }, [node('summary', {}, title), node('div', { class: 'disclosure-body' }, content)]);
}

function attemptDetails(exercise) {
  const attempts = exerciseAttempts(exercise.id).slice().sort((a, b) => text(b.createdAt).localeCompare(text(a.createdAt)));
  const body = node('div');
  if (!attempts.length) body.append(node('p', {}, 'No generation attempts recorded for this exercise. New jobs and their credit reservations will appear here after refresh.'));
  for (const attempt of attempts) {
    const spent = number(attempt.actualCredits), reserved = number(attempt.reservedCredits);
    const created = attempt.createdAt && !Number.isNaN(Date.parse(attempt.createdAt)) ? new Date(attempt.createdAt).toLocaleString() : null;
    const item = node('div', { class: 'attempt-row' }, [
      node('strong', {}, attempt.shot || attempt.id || 'Generation attempt'),
      node('span', {}, titleCase(attempt.status || 'Pending')),
      node('div', { class: 'attempt-meta' }, [node('span', {}, assetEdition(attempt)), attempt.model && node('span', {}, attempt.model), created && node('span', {}, created), node('span', {}, spent === null ? `${reserved ?? 'Unknown'} credits reserved` : `${spent} credits spent`), attempt.jobId && node('span', {}, `Job ${attempt.jobId}`)]),
    ]);
    if (attempt.notes) item.append(node('p', { class: 'attempt-meta' }, attempt.notes));
    body.append(item);
  }
  return disclosure(`Generation attempts${attempts.length ? ` (${attempts.length})` : ''}`, body);
}

function promptDetails(exercise, asset) {
  const attempts = exerciseAttempts(exercise.id);
  const matchingAttempts = attempts.filter(attempt => !ui.round || assetRoundId(attempt) === ui.round);
  const relevant = asset ? attempts.find(attempt => attempt.id === asset.attemptId || attempt.id === (asset.sourceAttemptId || asset.edit?.sourceAttemptId) || list(attempt.assetIds).includes(asset.id)) : matchingAttempts[matchingAttempts.length - 1];
  const prompts = list(ui.data.prompts).filter(prompt => prompt.exerciseId === exercise.id && (!ui.round || assetRoundId(prompt) === ui.round));
  const body = node('div');
  const prompt = asset?.promptText || asset?.prompt || relevant?.prompt || exercise.prompt;
  const source = asset?.promptFile || relevant?.promptFile;
  body.append(facts([
    ['Style version', asset?.styleVersion || ui.data.styleVersion || null], ['Prompt version', asset?.promptVersion || relevant?.promptVersion || null], ['Prompt file', source],
    ['Reference assets', list(asset?.referenceIds).join(', ')],
    ['Reference files', list(relevant?.references).map(reference => reference.path || reference.id || '').filter(Boolean).join(', ')],
  ]));
  function addPrompt(value, label) {
    if (label) body.append(node('h3', {}, label));
    body.append(node('pre', { class: 'prompt-text' }, value));
    const button = node('button', { type: 'button', class: 'text-button copy-prompt', on: { click: async () => {
      try { await navigator.clipboard.writeText(text(value)); button.textContent = 'Prompt copied'; announce('Prompt copied.'); }
      catch { button.textContent = 'Select the prompt text to copy it'; }
    } } }, 'Copy prompt');
    body.append(button);
  }
  if (prompt) addPrompt(prompt);
  else if (prompts.length) for (const entry of prompts) addPrompt(entry.text || entry.prompt || '', entry.shot || entry.path || 'Prompt');
  else body.append(node('p', {}, source ? 'The recorded prompt file is listed above. Full text will appear when the generation attempt is recorded.' : 'No exercise-specific prompt is recorded yet. The shared visual standard is available below.'));
  return disclosure('Prompt & references', body);
}

function assetDetails(asset) {
  if (!asset) return null;
  const link = asset.kind === 'external' ? safeExternalUrl(asset.url) : safeMediaUrl(asset.url);
  const edit = asset.edit;
  const sourceAttemptId = edit?.sourceAttemptId || asset.sourceAttemptId;
  const sourceAttempt = list(ui.data.attempts).find(attempt => attempt.id === sourceAttemptId);
  const editFacts = edit ? [
    ['Source asset', edit.sourceAssetId], ['Source generation attempt', sourceAttemptId],
    ['Source generation credits', number(sourceAttempt?.actualCredits) === null ? 'Not settled or not recorded' : `${fmtNumber(sourceAttempt.actualCredits)} credits`],
    ['Edit generation credits', number(edit.generationCredits) === null ? 'Not recorded' : `${fmtNumber(edit.generationCredits)} credits`],
    ['Edited source interval', number(edit.trimStartSeconds) !== null && number(edit.trimEndSeconds) !== null ? `${fmtNumber(edit.trimStartSeconds)}–${fmtNumber(edit.trimEndSeconds)} seconds` : null],
    ['Added start hold', number(edit.leadHoldSeconds) === null ? null : `${fmtNumber(edit.leadHoldSeconds)} seconds`],
    ['Added end hold', number(edit.tailHoldSeconds) === null ? null : `${fmtNumber(edit.tailHoldSeconds)} seconds`],
    ['Playback rate', number(edit.playbackRate) === null ? null : `${fmtNumber(edit.playbackRate)}×`],
  ] : [];
  return disclosure('Asset record', facts([
    ['Asset ID', asset.id], ['Round', roundLabel(assetRoundId(asset))], ['Style', asset.styleLabel || titleCase(asset.styleId) || 'Original style'], ['Shot', asset.shot], ['Source', asset.source], ['Rights', asset.license], ['Content decision', statusNames[asset.reviewStatus] || 'Pending'],
    ['Size', asset.kind === 'external' ? null : fmtBytes(asset.bytes)],
    ['Dimensions', asset.width && asset.height ? `${asset.width} × ${asset.height} px` : null],
    ['Duration', number(asset.durationSeconds) > 0 ? `${asset.durationSeconds} seconds` : null],
    ...editFacts,
    ['SHA-256', asset.sha256], ['File', link ? node('a', { href: link, target: '_blank', rel: 'noopener noreferrer' }, asset.kind === 'external' ? 'Open publisher reference' : 'Open local asset') : null],
  ]));
}

function reviewEvidence(exercise, asset) {
  const target = asset || exercise;
  if (!asset && !target.editorialReview && !target.trainerReview) return null;
  const section = node('section', { class: 'review-evidence', 'aria-label': asset ? 'Selected asset review evidence' : 'Exercise review evidence' }, [
    node('h3', {}, 'Review evidence'),
    node('p', { class: 'subtle' }, asset ? 'For the candidate currently shown.' : 'For the written exercise guidance.'),
  ]);
  const observations = [];
  for (const [label, record] of [['Editorial', target.editorialReview], ['Trainer', target.trainerReview]]) {
    const group = node('div', { class: 'evidence-entry' });
    const identity = record ? [
      record.reviewerType === 'ai' ? 'AI' : record.reviewerType === 'human' ? 'Human' : null,
      record.reviewer,
    ].filter(Boolean).join(' · ') : '';
    group.append(node('div', { class: 'evidence-heading' }, [
      node('strong', {}, label),
      node('span', {}, record ? (statusNames[record.status] || titleCase(record.status) || 'Recorded') : 'Not recorded'),
    ]));
    if (identity) group.append(node('p', { class: 'subtle' }, identity));
    if (record?.reviewedAt) {
      const date = new Date(record.reviewedAt);
      group.append(node('p', { class: 'subtle' }, Number.isNaN(date.getTime()) ? text(record.reviewedAt) : date.toLocaleString()));
    }
    if (record?.notes) {
      const notes = node('p', { class: 'evidence-notes' }, record.notes);
      if (text(record.notes).length > 400) {
        observations.push(node('details', { class: 'evidence-disclosure' }, [
          node('summary', {}, `Read ${label.toLowerCase()} observations`), notes,
        ]));
      } else group.append(notes);
    }
    section.append(group);
  }
  section.append(...observations);
  return section;
}

function candidateRoundControl(exercise) {
  const select = node('select', { id: 'candidate-round', 'aria-label': 'Candidate round', on: { change: event => {
    ui.round = event.target.value;
    ui.previews.delete(exercise.id);
    renderDetail();
  } } }, [
    ...list(ui.data.rounds).map(round => node('option', { value: round.id }, `${roundLabel(round.id)}${round.id === activeRoundId() ? ' · Current round' : ''}`)),
    node('option', { value: '' }, 'All rounds'),
  ]);
  select.value = ui.round || '';
  return node('label', { class: 'form-field candidate-round-control' }, ['Candidate round', select]);
}

function styleChoices(exercise, assets, active) {
  const styles = new Map(assets.filter(asset => asset.styleId).map(asset => [asset.styleId, asset.styleLabel || titleCase(asset.styleId)]));
  if (styles.size < 2) return null;
  const group = node('fieldset', { class: 'style-choices' }, node('legend', {}, 'Render style'));
  const buttons = node('div', { class: 'style-choice-buttons' });
  for (const [id, label] of styles) buttons.append(node('button', {
    type: 'button', class: 'style-choice', 'aria-pressed': String(active?.styleId === id),
    on: { click: () => {
      const candidates = assets.filter(asset => asset.styleId === id);
      const preferred = defaultAsset(exercise, candidates);
      ui.previews.set(exercise.id, preferred.id);
      renderDetail();
    } },
  }, label));
  group.append(buttons);
  return group;
}

function previousRoundFeedback(exercise) {
  const previous = exerciseHistory(exercise.id).find(entry => entry.roundId !== activeRoundId());
  if (!previous) return null;
  const available = exerciseAssets(exercise.id).filter(asset => assetRoundId(asset) === previous.roundId);
  const section = node('section', { class: 'previous-round-review', 'aria-label': 'Previous round feedback' }, [
    node('h3', {}, `${roundLabel(previous.roundId)} feedback`),
    node('p', { class: 'subtle' }, `${statusNames[previous.reviewStatus] || 'Pending'} · Preserved from the previous round`),
    previous.notes ? node('p', { class: 'evidence-notes' }, previous.notes) : node('p', { class: 'evidence-notes' }, 'The earlier decision and selected assets remain in review history.'),
  ]);
  if (available.length) section.append(node('button', { type: 'button', class: 'text-button', on: { click: () => {
    const selected = available.find(asset => list(previous.selectedAssetIds).includes(asset.id)) || available[0];
    // Keep the current candidate visible and open prior work alongside it.
    ui.round = activeRoundId();
    ui.comparisons.set(exercise.id, selected.id);
    renderDetail();
    document.querySelector('.comparison')?.scrollIntoView({ block: 'nearest' });
  } } }, 'Compare earlier media'));
  return section;
}

function reviewHistoryDetails(exercise) {
  const history = exerciseHistory(exercise.id);
  const body = node('div');
  if (!history.length) body.append(node('p', {}, 'Saved decisions will appear here, with the round, selected assets, and original notes.'));
  const assets = new Map(exerciseAssets(exercise.id).map(asset => [asset.id, asset]));
  for (const entry of history) {
    const created = entry.createdAt && !Number.isNaN(Date.parse(entry.createdAt)) ? new Date(entry.createdAt).toLocaleString() : null;
    const item = node('div', { class: 'attempt-row' }, [
      node('strong', {}, roundLabel(entry.roundId || 'round-1')),
      node('span', {}, statusNames[entry.reviewStatus] || 'Pending'),
      node('div', { class: 'attempt-meta' }, [created && node('span', {}, created), node('span', {}, entry.source === 'dashboard' ? 'Saved locally' : 'Preserved round decision')]),
    ]);
    if (entry.notes) item.append(node('p', { class: 'history-notes' }, entry.notes));
    const selected = list(entry.selectedAssetIds).map(id => {
      const asset = assets.get(id);
      return asset ? `${asset.title || id} (${assetEdition(asset)})` : id;
    });
    item.append(node('p', { class: 'history-selection' }, selected.length ? `Selected: ${selected.join('; ')}` : 'No assets selected.'));
    body.append(item);
  }
  return disclosure(`Review history${history.length ? ` (${history.length})` : ''}`, body);
}

function renderDetail() {
  const exercise = currentExercise();
  const main = $('exercise-detail');
  main.setAttribute('aria-busy', 'false');
  if (!exercise) {
    main.replaceChildren(node('div', { class: 'blank-detail' }, [node('h2', {}, 'Find an exercise to review'), node('p', {}, 'Adjust the search or filters to bring exercises back into the queue.'), node('button', { class: 'text-button', type: 'button', on: { click: clearFilters } }, 'Clear search and filters')]));
    return;
  }
  const allAssets = exerciseAssets(exercise.id);
  const assets = allAssets.filter(asset => visibleInRound(asset, exercise));
  const active = previewAsset(exercise, assets);
  const rows = filteredExercises(), index = rows.findIndex(row => row.id === exercise.id);
  const navigation = node('div', { class: 'detail-navigation', 'aria-label': 'Navigate exercise queue' }, [
    node('button', { type: 'button', class: 'icon-button', disabled: index <= 0, 'aria-label': 'Previous exercise', on: { click: () => selectExercise(rows[index - 1].id, true) } }, icon('previous')),
    node('button', { type: 'button', class: 'icon-button', disabled: index < 0 || index >= rows.length - 1, 'aria-label': 'Next exercise', on: { click: () => selectExercise(rows[index + 1].id, true) } }, icon('next')),
  ]);
  const header = node('div', { class: 'detail-header' }, [node('div', {}, [node('h2', { class: 'detail-title' }, exercise.name), node('div', { class: 'exercise-meta' }, [
    node('span', {}, list(exercise.metadata?.equipment).join(', ') || 'Equipment unspecified'),
    node('span', {}, titleCase(exercise.metadata?.difficulty || '')), node('span', {}, exercise.pilot ? 'Pilot sample' : 'Catalog exercise'),
    exercise.compound === true && node('span', {}, 'Compound'),
    exercise.bodyPosition && node('span', {}, titleCase(exercise.bodyPosition)),
  ])]), navigation]);
  const media = node('section', { class: 'media-column', 'aria-label': 'Form media preview' }, [
    node('div', { class: 'section-heading' }, [node('h2', {}, active ? 'Review the study' : 'Form preview'), node('span', { class: `status-label ${queueStatus(exercise)}` }, `${mediaUpdateLabel(exercise)} · ${statusNames[queueStatus(exercise)]}`)]),
    ['needs-correction', 'quality-hold', 'provider-failed'].includes(exercise.productionStatus) && exercise.productionNote && node('p', { class: 'review-caution' }, `No cleared video candidate: ${exercise.productionNote}`),
    candidateRoundControl(exercise), styleChoices(exercise, assets, active), mediaPreview(exercise, active), assetFacts(active), candidateControls(exercise, assets, active, allAssets), reviewEvidence(exercise, active),
  ]);
  const guidance = node('div', { class: 'guidance-column' }, [
    node('section', { class: 'recommendation' }, [node('h2', {}, 'Teaching approach'), node('span', { class: 'format-title' }, formatNames[exercise.teachingFormat] || 'Not classified'), node('p', {}, exercise.rationale || 'Review the instructions and choose the simplest medium that clearly explains the movement.'), node('span', { class: 'status-label' }, recommendationNames[exercise.recommendationStatus] || recommendationNames.provisional)]),
    node('section', { class: 'guidance-section' }, [node('h2', {}, 'Form guidance'), list(exercise.instructions).length ? node('ol', { class: 'instructions' }, exercise.instructions.map(step => node('li', {}, step))) : node('p', { class: 'review-caution' }, 'No instructions are available in this catalog record.')]),
  ]);
  const primary = list(exercise.metadata?.primaryMuscles), secondary = list(exercise.metadata?.secondaryMuscles);
  if (primary.length || secondary.length) guidance.append(node('div', { class: 'muscle-legend' }, [
    primary.length ? node('div', { class: 'muscle-line' }, [node('span', { class: 'swatch', 'aria-hidden': 'true' }), node('div', {}, [node('strong', {}, 'Primary: '), node('span', {}, primary.join(', '))])]) : null,
    secondary.length ? node('div', { class: 'muscle-line supporting' }, [node('span', { class: 'swatch', 'aria-hidden': 'true' }), node('div', {}, [node('strong', {}, 'Supporting: '), node('span', {}, secondary.join(', '))])]) : null,
  ]));
  guidance.append(reviewForm(exercise));
  const details = node('section', { class: 'details-section', 'aria-label': 'Production details' }, [
    reviewHistoryDetails(exercise), promptDetails(exercise, active), attemptDetails(exercise), assetDetails(active),
    disclosure('Shared visual standard', ui.data.style ? node('pre', { class: 'prompt-text' }, ui.data.style) : node('p', {}, 'The shared visual standard has not been added yet. Refresh when it is available.')),
    disclosure('Queue & credit accounting', [node('p', {}, 'Each exercise keeps its review decision, selected assets, and notes. Refresh reads work completed by the generation tool; it preserves your unsaved notes in this window.'), node('p', { class: 'queue-details' }, 'Reserved credits remain held until an attempt has a recorded settlement. The workbench does not submit generations or spend credits.'), facts([['Canonical ID', exercise.id], ['Priority', exercise.priority], ['Catalog', `${text(ui.data.catalog?.version)} · revision ${text(ui.data.catalog?.revision)}`]])]),
  ]);
  main.replaceChildren(header, ...[previousRoundFeedback(exercise)].filter(Boolean), node('div', { class: 'review-layout' }, [media, guidance]), details);
  updateSelectionSummary(exercise);
}

function populateFilters() {
  $('filter-generated-round').replaceChildren(node('option', { value: '' }, 'All generation rounds'), ...list(ui.data.rounds).slice().reverse().map(round => node('option', { value: round.id }, roundLabel(round.id))));
  $('filter-generated-round').value = ui.generatedRound;
  const activities = [...new Set(ui.data.exercises.flatMap(exercise => list(exercise.metadata?.activities)))].sort();
  $('filter-activity').replaceChildren(node('option', { value: '' }, 'All activities'), ...activities.map(activity => node('option', { value: activity }, titleCase(activity))));
  $('filter-activity').value = ui.activity;
  const formats = [...new Set(ui.data.exercises.map(exercise => exercise.teachingFormat).filter(Boolean))];
  $('filter-format').replaceChildren(node('option', { value: '' }, 'All formats'), ...Object.keys(formatNames).filter(format => formats.includes(format)).map(format => node('option', { value: format }, formatNames[format])));
  $('filter-format').value = ui.format;
}

async function loadState() {
  if (ui.loading || ui.saving.size) return;
  ui.loading = true; $('refresh').disabled = true; $('refresh').textContent = 'Refreshing…'; $('load-error').hidden = true;
  try {
    const response = await fetch('/api/state', { cache: 'no-store', headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error(`The local server returned ${response.status}.`);
    const data = await response.json();
    if (!Array.isArray(data.exercises) || !data.exercises.every(exercise => exercise && typeof exercise.id === 'string' && typeof exercise.name === 'string')) throw new Error('The local server returned an unreadable exercise catalog.');
    for (const [id, draft] of ui.drafts) if (!draft.dirty) ui.drafts.delete(id);
    const previousActiveRound = activeRoundId();
    ui.data = data;
    if (ui.round === null || (ui.round === previousActiveRound && previousActiveRound !== activeRoundId())) ui.round = activeRoundId();
    if (ui.round && !list(data.rounds).some(round => round.id === ui.round)) ui.round = activeRoundId();
    if (!ui.selectedId) {
      let hash = ''; try { hash = decodeURIComponent(location.hash.slice(1)); } catch { /* Ignore an invalid bookmark. */ }
      const bookmarked = data.exercises.find(exercise => exercise.id === hash);
      if (bookmarked) { ui.selectedId = bookmarked.id; if (!bookmarked.pilot) ui.scope = 'all'; }
    }
    populateFilters(); renderSummary();
    const available = filteredExercises();
    if (!available.some(exercise => exercise.id === ui.selectedId)) ui.selectedId = available.find(exercise => exercise.id === 'ex_bench_press')?.id || available[0]?.id || null;
    syncExerciseHash();
    renderList(); renderDetail(); announce('Exercise media queue refreshed.');
  } catch (error) {
    const message = `${error.message || 'The media queue could not be loaded.'} Keep the local form-media server running, then retry.`;
    $('load-error').replaceChildren(node('span', {}, message), node('button', { type: 'button', class: 'button secondary', on: { click: loadState } }, 'Retry loading'));
    $('load-error').hidden = false;
    if (!ui.data) {
      $('queue-progress').textContent = 'Review queue unavailable'; $('catalog-version').textContent = 'Local server unavailable';
      $('exercise-list').replaceChildren(node('p', { class: 'empty-results' }, 'Connect to the local server to load the exercise catalog.'));
      $('exercise-list').setAttribute('aria-busy', 'false'); $('exercise-detail').setAttribute('aria-busy', 'false');
      $('exercise-detail').replaceChildren(node('div', { class: 'blank-detail' }, [node('h2', {}, 'Your review queue is not connected'), node('p', {}, 'Start the local media server and retry. No review decisions have been changed.')]));
    }
  } finally { ui.loading = false; $('refresh').disabled = false; $('refresh').textContent = 'Refresh'; }
}

$('refresh').addEventListener('click', loadState);
$('search').addEventListener('input', event => { ui.search = event.target.value; if (ui.data) applyFilters(); });
$('scope-pilot').addEventListener('click', () => { ui.scope = 'pilot'; if (ui.data) applyFilters(); });
$('scope-all').addEventListener('click', () => { ui.scope = 'all'; if (ui.data) applyFilters(); });
for (const key of ['activity', 'format', 'status']) $('filter-' + key).addEventListener('change', event => { ui[key] = event.target.value; if (ui.data) applyFilters(); });
$('filter-generated-round').addEventListener('change', event => { ui.generatedRound = event.target.value; ui.scope = 'all'; ui.round = ui.generatedRound; if (ui.data) applyFilters(); });
$('show-needs-review').addEventListener('click', () => { ui.scope = 'all'; ui.status = 'needs-review'; ui.generatedRound = ''; ui.round = ''; $('filter-status').value = ui.status; $('filter-generated-round').value = ''; if (ui.data) applyFilters(); });
$('clear-filters').addEventListener('click', () => { if (ui.data) clearFilters(); });
$('catalog-toggle').addEventListener('click', () => setCatalogOpen($('catalog-toggle').getAttribute('aria-expanded') !== 'true'));
window.addEventListener('hashchange', navigateToHash);
window.addEventListener('beforeunload', event => { if ([...ui.drafts.values()].some(draft => draft.dirty) || ui.saving.size) { event.preventDefault(); event.returnValue = ''; } });
void loadState();
