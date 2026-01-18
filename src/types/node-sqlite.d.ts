declare module 'node:sqlite' {
    export class DatabaseSync {
        constructor(filename: string, options?: any);
        exec(sql: string): any;
        prepare(sql: string): StatementSync;
    }

    export class StatementSync {
        all(params?: any[]): any[];
        run(params?: any[]): any;
        get(params?: any[]): any | null;
    }
}