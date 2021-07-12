const guildSocket = new WebSocket(
    websocket_protocol + '://' + window.location.host + '/ws/chat/' + guildId + '/'
);

guildSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);

    if (data.action === 'kicked' || data.action === 'banned') {
        document.getElementById(`id_${data.member.id}`).remove();
    } else if (data.action === 'joined') {
        const list = document.querySelector(`#members-list`);

        let admin_check = ``;
        if (data.member.admin) {
            admin_check = `checked`;
        }
        let bot_check = ``;
        if (data.member.bot) {
            bot_check = `checked`;
        }

        let change_success =
            `<div style="display: flex">` +
            `<a href="/guild/${ guildId }/change/members/${data.member.id}/kick/" style="margin-right: 15px" class="btn btn-warning">Выгнать</a>` +
            `<a href="/guild/${ guildId }/change/members/${data.member.id}/ban/" class="btn btn-danger">Забанить</a>` +
            `</div>`;
        let change = ``;
        if (!data.member.admin) {
            change = change_success;
        }

        if (user_id === guild_creator_id && user_id !== data.member.user) {
            change = change_success;
        }

        list.innerHTML +=
            `<div id="id_${data.member.id}" class="card" style="margin-top: 10px; margin-bottom: 5px">` +
            `<div class="card-header">` +
            `${data.member.username}` +
            `</div>` +
            `<div class="card-body" style="height: 70px">` +
            `<div style="display: flex; justify-content: space-between; align-items: center; height: 38px">` +
            `<div>` +
            `<div class="form-check">` +
            `<label class="form-check-label" for="id_admin_check">Администратор</label>` +
            `<input type="checkbox" ${admin_check} name="admin_check" class="form-check-input" id="id_admin_check" disabled>` +
            `</div>` +
            `<div class="form-check">` +
            `<label class="form-check-label" for="id_bot_check">Бот</label>` +
            `<input type="checkbox" ${bot_check} name="bot_check" class="form-check-input" id="id_bot_check" disabled>` +
            `</div>` +
            `</div>` +
            `${change}` +
            `</div>` +
            `</div>` +
            `</div>`;
    }
};