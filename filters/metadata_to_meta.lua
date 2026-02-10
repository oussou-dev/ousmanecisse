function Meta(m)
    -- The metadata is accessible in m
    -- We want to inject a raw HTML block into the document if translation-url is present
    if m["translation-url"] then
        local content = pandoc.utils.stringify(m["translation-url"])
        -- Use quarto.doc.include_text("in-header", ...) is available in 1.4+
        -- But for standard Lua filter:
        return m
    end
    return m
end

function Pandoc(doc)
    local meta = doc.meta
    if meta['translation-url'] then
        local url = pandoc.utils.stringify(meta['translation-url'])
        local raw = '<meta name="translation-url" content="' .. url .. '">'
        -- Insert into header includes? No, just raw HTML block at start of body,
        -- but scripts look for it in DOM so that's fine.
        -- Ideally, we put it in header-includes but that's harder from Lua filter without Quarto API.
        -- Putting it at the beginning of the body is sufficient for JS querySelector.
        table.insert(doc.blocks, 1, pandoc.RawBlock('html', raw))
    end
    return doc
end
