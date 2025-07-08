function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verifica si el cookie empieza con el nombre que queremos
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCSRFTokenFromInput() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : null;
}

function get_cite(text){
    const path = window.location.pathname;
    const match = path.match(/edit\/(\d+)\//);  // Extrae el número entre 'edit/' y el siguiente '/'
    var pk_register = parseInt(match[1], 10);

    return fetch('/admin/extract-citation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFTokenFromInput()
        },
        body: JSON.stringify({ 
                                text: text,
                                pk: pk_register
                            })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Cita extraída:", data);
        return data.refid;
        // Aquí podrías hacer algo con los resultados
    })
    .catch(error => {
        console.error("Error al extraer citas:", error);
    });
}


document.addEventListener("DOMContentLoaded", function () {
    var tab = document.querySelector('a[role="tab"][aria-selected="true"]');
    if(tab.id !== 'tab-label-body'){
        return false;
    }

    // Espera a que el campo se cargue
    document.querySelectorAll('textarea').forEach(function (textarea) {
        if(textarea.value.length < 50){
            return false;
        }
        // Crea el botón
        const button = document.createElement('button');
        button.type = 'button';
        button.innerText = 'Añadir <xref>';
        button.style.margin = '5px';

        // Acción al hacer clic
        button.addEventListener('click', function () {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const selectedText = textarea.value.substring(start, end);

            if (!selectedText) {
                alert('Selecciona un texto para aplicar <xref>');
                return;
            }

            var textClean = selectedText.replace('[style name="italic"]','').replace('[/style]','');
            //var cite = get_cite(textClean);

            get_cite(textClean).then(cite => {
                // aquí ya tienes el valor real
                const xrefWrapped = `<xref reftype="bibr" rid="${cite}">${selectedText}</xref>`;
                const newText = textarea.value.slice(0, start) + xrefWrapped + textarea.value.slice(end);
                textarea.value = newText;
            });

        });

        // Agrega el botón justo después del textarea
        textarea.parentNode.insertBefore(button, textarea.nextSibling);
    });
});


document.addEventListener("DOMContentLoaded", function () {
    var path = window.location.pathname;
    // Busca el campo por su ID (ajústalo si es diferente)
    if ( path.indexOf('markupxml/edit') == -1 ){
        return false;
    }
    var ids = ['collection', 'journal_title', 'short_title', 'title_nlm', 'acronym', 'issn', 'pissn', 'eissn', 'pubname']
    $.each(ids, function(i, val){
        const collectionField = document.querySelector('#id_'+val);
        if (collectionField) {
            collectionField.setAttribute('readonly', true);  // Solo lectura
            collectionField.classList.add('disabled');        // Para aplicar estilo visual
            // Agregar estilos Wagtail para apariencia "inactiva"
            collectionField.style.backgroundColor = 'var(--w-color-surface-field-inactive)';
            collectionField.style.borderColor = 'var(--w-color-border-field-inactive)';
            collectionField.style.color = 'var(--w-color-text-placeholder)';
            collectionField.style.cursor = 'not-allowed';
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const journalInput = document.querySelector("#id_journal");

    //if (!journalInput) return;

    // MutationObserver para detectar cambios en la selección del widget
    const journalWrapper = document.querySelector('[data-autocomplete-input-id="id_journal"]');

    if (!journalWrapper) return;

    const observer = new MutationObserver(() => {
        // Buscar el input hidden que contiene el valor
        const hiddenInput = journalWrapper.querySelector('input[type="hidden"][name="journal"]');
        if (!hiddenInput) return;
        
        let journalValue;

        try {
            journalValue = JSON.parse(hiddenInput.value);
        } catch (e) {
            return;
        }

        if (journalValue && journalValue.pk) {
            
            fetch('/admin/get_journal/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFTokenFromInput()
                },
                body: JSON.stringify({ 
                                        pk: journalValue.pk
                                    })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                $('#id_journal_title').val(data.journal_title);
                $('#id_short_title').val(data.short_title);
                $('#id_title_nlm').val(data.title_nlm);
                $('#id_acronym').val(data.acronym);
                $('#id_issn').val(data.issn);
                $('#id_pissn').val(data.pissn);
                $('#id_eissn').val(data.eissn);
                $('#id_pubname').val(data.pubname);
            })
            .catch(error => {
                console.error("Error:", error);
                $('#id_journal_title').val("");
                $('#id_short_title').val("");
                $('#id_title_nlm').val("");
                $('#id_acronym').val("");
                $('#id_issn').val("");
                $('#id_pissn').val("");
                $('#id_eissn').val("");
                $('#id_pubname').val("");
            });

        }else{
            $('#id_journal_title').val("");
            $('#id_short_title').val("");
            $('#id_title_nlm').val("");
            $('#id_acronym').val("");
            $('#id_issn').val("");
            $('#id_pissn').val("");
            $('#id_eissn').val("");
            $('#id_pubname').val("");
        }
    });

    observer.observe(journalWrapper, { childList: true, subtree: true });
});




