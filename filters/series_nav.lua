-- series_nav.lua
-- Quarto Lua filter to add "Previous / Next" navigation links for post series.
--
-- Usage: Add these fields to your post's YAML frontmatter:
--   series-name: "AI Dev Tools"
--   series-prev-url: "/posts/ai-dev-tools-week-1/"
--   series-prev-title: "Week 1 - Vibe Coding & Foundations"
--   series-next-url: "/posts/ai-dev-tools-week-3/"
--   series-next-title: "Week 3 - MCP & Agents"
--
-- Only series-name is required. prev/next are optional (omit if first/last post).

function Pandoc(doc)
    local meta = doc.meta

    -- Only proceed if this post belongs to a series
    if not meta["series-name"] then
        return doc
    end

    local series_name = pandoc.utils.stringify(meta["series-name"])
    local lang = "en"
    if meta["lang"] then
        lang = pandoc.utils.stringify(meta["lang"])
    end

    -- Read optional prev/next metadata
    local prev_url = nil
    local prev_title = nil
    local next_url = nil
    local next_title = nil

    if meta["series-prev-url"] then
        prev_url = pandoc.utils.stringify(meta["series-prev-url"])
    end
    if meta["series-prev-title"] then
        prev_title = pandoc.utils.stringify(meta["series-prev-title"])
    end
    if meta["series-next-url"] then
        next_url = pandoc.utils.stringify(meta["series-next-url"])
    end
    if meta["series-next-title"] then
        next_title = pandoc.utils.stringify(meta["series-next-title"])
    end

    -- If there's nothing to link, skip
    if not prev_url and not next_url then
        return doc
    end

    -- Labels based on language
    local label_series, label_prev, label_next
    if lang == "fr" then
        label_series = "Série"
        label_prev = "← Article précédent"
        label_next = "Article suivant →"
    else
        label_series = "Series"
        label_prev = "← Previous post"
        label_next = "Next post →"
    end

    -- Build the HTML navigation block
    local html = '<div class="series-nav">\n'
    html = html .. '  <div class="series-nav-header">\n'
    html = html .. '    <span class="series-nav-badge">' .. label_series .. '</span>\n'
    html = html .. '    <span class="series-nav-name">' .. series_name .. '</span>\n'
    html = html .. '  </div>\n'
    html = html .. '  <div class="series-nav-links">\n'

    -- Previous link
    if prev_url and prev_title then
        html = html .. '    <a href="' .. prev_url .. '" class="series-nav-link series-nav-prev">\n'
        html = html .. '      <span class="series-nav-label">' .. label_prev .. '</span>\n'
        html = html .. '      <span class="series-nav-title">' .. prev_title .. '</span>\n'
        html = html .. '    </a>\n'
    else
        -- Empty spacer to keep flex layout correct
        html = html .. '    <div class="series-nav-spacer"></div>\n'
    end

    -- Next link
    if next_url and next_title then
        html = html .. '    <a href="' .. next_url .. '" class="series-nav-link series-nav-next">\n'
        html = html .. '      <span class="series-nav-label">' .. label_next .. '</span>\n'
        html = html .. '      <span class="series-nav-title">' .. next_title .. '</span>\n'
        html = html .. '    </a>\n'
    else
        html = html .. '    <div class="series-nav-spacer"></div>\n'
    end

    html = html .. '  </div>\n'
    html = html .. '</div>\n'

    -- Append navigation block at the end of the document
    table.insert(doc.blocks, pandoc.RawBlock('html', html))

    return doc
end
