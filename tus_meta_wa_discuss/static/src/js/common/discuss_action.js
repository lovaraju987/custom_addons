/* @odoo-module */

import { DiscussClientAction } from "@mail/core/web/discuss_client_action";

import { patch } from "@web/core/utils/patch";

patch(DiscussClientAction.prototype, {

    async restoreDiscussThread(props) {
        await this.messaging.isReady;
        if (this.store.inPublicPage) {
            return;
        }
        const rawActiveId = !props.action.context.params?._company_switching
            ? (props.action.context.active_id ??
               props.action.params?.active_id ??
               this.store.Thread.localIdToActiveId(this.store.discuss.thread?.localId) ??
               "mail.box_inbox")
            : "mail.box_inbox";
        const activeId =
            typeof rawActiveId === "number" ? `discuss.channel_${rawActiveId}` : rawActiveId;
        let [model, id] = activeId.split("_");
        if (model === "mail.channel") {
            // legacy format (sent in old emails, shared links, ...)
            model = "discuss.channel";
        }
        let activeThread = this.store.Thread.get({ model, id });
        if (!activeThread?.type && model === "discuss.channel") {
            activeThread = await this.threadService.fetchChannel(parseInt(id));
        }
        if (activeThread && activeThread.notEq(this.store.discuss.thread)) {
            this.threadService.setDiscussThread(activeThread, false);
        }
        this.store.discuss.hasRestoredThread = true;
    }

})
