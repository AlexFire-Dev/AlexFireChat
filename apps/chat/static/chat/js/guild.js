let loading = false;

const guildSocket = new WebSocket(
     websocket_protocol + '://' + window.location.host + '/ws/chat/' + guildId + '/'
);

guildSocket.onclose = function (e) {
    document.location.href = redirect_url;
};

guildSocket.onopen = function (e) {
    const feed = document.querySelector(`#feed`);
    if (page > 1 && feed.scrollTop <= 100 && !loading) {
        loading = true;
        page = page - 1;

        guildSocket.send(JSON.stringify({
            'action': 'load',
            'page_id': page,
        }));
    }
};

guildSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);


    if (data.action === 'send') {
        const feed = document.querySelector(`#feed`);

        let text = data.message.text.replace(/\n/g, '<br>');

        const created_at = moment(moment.utc(data.message.created_at, 'YYYY-MM-DD HH:mm').toDate()).local().format('DD.MM.YYYY HH:mm');
        const modified_at = moment(moment.utc(data.message.modified_at, 'YYYY-MM-DD HH:mm').toDate()).local().format('DD.MM.YYYY HH:mm');

        let href = ''

        if (data.author.id === member_id || true === member_admin) {
            href = `<button class="deleteButton" onclick="deleteMessage(${data.message.id})" type="button" href="#"><img src="${delete_url}" alt="delete" width="21px" height="21px"></button>`;
        }

        feed.innerHTML +=
            `<div id="id_${data.message.id}" class="card text-center" style="margin-top: 15px">` +
            `<header class="card-header" style="display: flex; flex-grow: 1; justify-content: space-between; align-items: center">` +
            `<span style="font-weight: bold">${data.author.nickname}</span>` +
            `${href}` +
            `</header>` +
            `<div class="card-body">` +
            `<p class="card-text" style="text-align: start">${text}</p>` +
            `</div>` +
            `<footer class="card-footer text-muted" style="display: flex; align-items: flex-start; justify-content: space-between">` +
            `<span class="text-muted" style="display: flex; font-size: 15px">Создано: <div class="local-time">${created_at}</div></span>` +
            `<span class="text-muted" style="display: flex; font-size: 15px">Обновлено: <div class="local-time">${modified_at}</div></span>` +
            `</footer>` +
            `</div>`;
        feed.scrollTop = feed.scrollHeight
    } else if (data.action === 'delete') {
        document.getElementById(`id_${data.message.id}`).remove();
    } else if (data.action === 'load') {
        const feed = document.querySelector(`#feed`);
        let html = '';
        for (let event of data.messages) {
            let text = event.message.text.replace(/\n/g, '<br>');

            const created_at = moment(moment.utc(event.message.created_at, 'YYYY-MM-DD HH:mm').toDate()).local().format('DD.MM.YYYY HH:mm');
            const modified_at = moment(moment.utc(event.message.modified_at, 'YYYY-MM-DD HH:mm').toDate()).local().format('DD.MM.YYYY HH:mm');

            let href = ''
            if (event.author.id === member_id || true === member_admin) {
                href = `<button class="deleteButton" onclick="deleteMessage(${event.message.id})" type="button" href="#"><img src="${delete_url}" alt="delete" width="21px" height="21px"></button>`;
            }

            html +=
                `<div id="id_${event.message.id}" class="card text-center" style="margin-top: 15px">` +
                `<header class="card-header" style="display: flex; flex-grow: 1; justify-content: space-between; align-items: center">` +
                `<span style="font-weight: bold">${event.author.nickname}</span>` +
                `${href}` +
                `</header>` +
                `<div class="card-body">` +
                `<p class="card-text" style="text-align: start">${text}</p>` +
                `</div>` +
                `<footer class="card-footer text-muted" style="display: flex; align-items: flex-start; justify-content: space-between">` +
                `<span class="text-muted" style="display: flex; font-size: 15px">Создано: <div class="local-time">${created_at}</div></span>` +
                `<span class="text-muted" style="display: flex; font-size: 15px">Обновлено: <div class="local-time">${modified_at}</div></span>` +
                `</footer>` +
                `</div>`;
        }
        let scroll = feed.scrollHeight - feed.scrollTop;
        feed.innerHTML = html + feed.innerHTML;
        feed.scrollTop = feed.scrollHeight - scroll;
        loading = false;
    }
};

document.querySelector(`#TextMessageInput`).focus();
document.querySelector(`#TextMessageInput`).onkeyup = function (e) {
    if (e.keyCode === 13 && e.ctrlKey) {
        document.querySelector(`#TextMessageButton`).click();
    }
};

document.querySelector(`#TextMessageButton`).onclick = function (e) {
    const TextMessageInput = document.querySelector(`#TextMessageInput`);
    const message = TextMessageInput.value;

    if (message !== '') {
        guildSocket.send(JSON.stringify({
            'action': 'send',
            'message': message
        }));
    }

    TextMessageInput.value = '';
};

function deleteMessage(message_id) {
    guildSocket.send(JSON.stringify({
        'action': 'delete',
        'message_id': message_id,
    }));
}

document.addEventListener('DOMContentLoaded', function () {
    const feed = document.querySelector(`#feed`);
    feed.scrollTop = feed.scrollHeight;

    for (const dt of document.querySelectorAll('.local-time')) {
        const utcTime = moment.utc(dt.innerHTML, 'YYYY-MM-DD HH:mm').toDate();
        dt.innerHTML = moment(utcTime).local().format('DD.MM.YYYY HH:mm');
    }

    feed.onscroll = function () {
        if (page > 1 && feed.scrollTop <= 125 && !loading) {
            loading = true;
            page = page - 1;

            guildSocket.send(JSON.stringify({
                'action': 'load',
                'page_id': page,
            }));
        }
    }
});