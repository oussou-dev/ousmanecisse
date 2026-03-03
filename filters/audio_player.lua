function Pandoc(doc)
    -- On ne s'active que si le rendu est HTML (ignore PDF, Word, etc.)
    if not FORMAT:match('html') then
        return nil
    end

    -- 1. On récupère les métadonnées (injectées par notre script Python V2)
    local audio_short = doc.meta['audio-short']
    local audio_podcast = doc.meta['audio-podcast']

    if not audio_short and not audio_podcast then
        return nil
    end

    -- 2. Gestion de la langue pour l'UI (Bilingue dynamique)
    local lang = "en"
    if doc.meta.lang then
        lang = pandoc.utils.stringify(doc.meta.lang)
    end

    local i18n = {
        fr = {
            title = "Version Audio IA",
            short = "Résumé Rapide",
            long = "Deep Dive Podcast"
        },
        en = {
            title = "AI Audio Version",
            short = "Quick Summary",
            long = "Deep Dive Podcast"
        }
    }
    local t = i18n[lang] or i18n['en']

    -- 3. Création du bloc conteneur esthétique (Basé sur les variables CSS Bootstrap de Quarto pour gérer le Dark/Light mode natif)
    local html_content = [[
<div class="quarto-audio-container" style="background-color: var(--bs-tertiary-bg); border-left: 4px solid var(--bs-primary); padding: 1.2em; margin-bottom: 2em; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
  <h4 style="margin-top: 0; font-size: 1.1em; display: flex; align-items: center; gap: 8px; margin-bottom: 15px; color: var(--bs-heading-color);">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-headphones" viewBox="0 0 16 16">
      <path d="M8 3a5 5 0 0 0-5 5v1h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V8a6 6 0 1 1 12 0v5a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1V8a5 5 0 0 0-5-5z"/>
    </svg>
    %s
  </h4>
]]
    html_content = string.format(html_content, t.title)

    -- Fonction utilitaire de formatage (sec -> 1m27)
    local function format_duration(seconds)
        if not seconds then return "" end
        local m = math.floor(seconds / 60)
        local s = seconds % 60
        return string.format(" (%dm%02d)", m, s)
    end

    -- 4. Injection conditionnelle du Short
    if audio_short then
        local src = pandoc.utils.stringify(audio_short)
        local dur = doc.meta['duration-short'] and
            format_duration(tonumber(pandoc.utils.stringify(doc.meta['duration-short']))) or ""
        html_content = html_content .. string.format([[
<div style="margin-bottom: 12px;">
    <div style="font-size: 0.9em; font-weight: 600; margin-bottom: 6px; color: var(--bs-body-color);">⚡ %s%s</div>
    <audio controls style="width: 100%%; height: 40px; outline: none;" src="%s"></audio>
</div>
]], t.short, dur, src)
    end

    -- 5. Injection conditionnelle du Podcast
    if audio_podcast then
        local src = pandoc.utils.stringify(audio_podcast)
        local dur = doc.meta['duration-podcast'] and
            format_duration(tonumber(pandoc.utils.stringify(doc.meta['duration-podcast']))) or ""
        html_content = html_content .. string.format([[
<div>
    <div style="font-size: 0.9em; font-weight: 600; margin-bottom: 6px; color: var(--bs-body-color);">🎙️ %s%s</div>
    <audio controls style="width: 100%%; height: 40px; outline: none;" src="%s"></audio>
</div>
]], t.long, dur, src)
    end

    html_content = html_content .. "</div>"

    local raw_html = pandoc.RawBlock('html', html_content)

    -- 6. Injection juste après le premier titre de niveau 1 (Header 1)
    local target_pos = 1 -- Fallback si on ne trouve pas de H1

    for i, block in ipairs(doc.blocks) do
        if block.t == "Header" and block.level == 1 then
            target_pos = i + 1
            break
        end
    end

    table.insert(doc.blocks, target_pos, raw_html)

    return doc
end
